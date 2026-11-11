param(
    [ValidateRange(1, 24)][int]$Observations = 24,
    [ValidateRange(45, 180)][int]$IntervalSeconds = 180,
    [switch]$FollowPostrun
)

# Read-only administrative observation, not a model/controller restart.
# Keep one observer process and bind its handle to the original controller.
$ErrorActionPreference = 'Stop'
$controllerPid = 12928
$taskRoot = Join-Path (Split-Path -Parent $PSScriptRoot) '.local/agent-rd-run-20261110-v1'
$publicRoot = Join-Path (Split-Path -Parent $PSScriptRoot) 'docs/evidence/agent-rd-20261110-v1'
$observerProcess = [System.Diagnostics.Process]::GetCurrentProcess()
$observerProcess.ProcessorAffinity = [IntPtr]1
$controllerProcess = [System.Diagnostics.Process]::GetProcessById($controllerPid)
$controllerHandle = $controllerProcess.Handle
$controllerInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $controllerPid"
if ($controllerInfo.CommandLine -notlike '*agent_rd_admin_v1.py run locked-supervisor-host-resume-v1*' -or $controllerProcess.HasExited) {
    throw 'Expected original controller is not live; inspect authoritative state without restarting it.'
}
$controllerStarted = $controllerProcess.StartTime.ToUniversalTime().ToString('o')

try {
    for ($observation = 0; $observation -lt $Observations; $observation++) {
        $observerProcess.Refresh()
        # Cooperative control-overhead stop only; not a retrospective hard cap.
        if ($observerProcess.TotalProcessorTime.TotalSeconds -gt 15) {
            [pscustomobject]@{ observer_status = 'OBSERVER_CPU_SELF_STOP'; model_stop_requested = $false } | ConvertTo-Json -Compress
            break
        }
        if ($controllerProcess.HasExited) {
            [pscustomobject]@{ observer_status = 'ORIGINAL_CONTROLLER_EXITED'; verified_pid = $controllerPid; controller_started = $controllerStarted } | ConvertTo-Json -Compress
            break
        }
        try {
            $beat = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'supervisor-host-resume-v1/heartbeat.json') | ConvertFrom-Json
            $final = Test-Path -LiteralPath (Join-Path $publicRoot 'locked-progress-v1.json')
            $stepsCompleted = $null
            if ($FollowPostrun -and $final) {
                $disposition = Get-Content -Raw -LiteralPath (Join-Path $publicRoot 'locked-progress-v1.json') | ConvertFrom-Json
                $resource = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'jobs/locked-supervisor-host-resume-v1/resource.json') | ConvertFrom-Json
                $postrun = Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'postrun-documents-host-resume-v1/progress.json') | ConvertFrom-Json
                $beat.completed = $disposition.attempted_units
                $beat.utc = $resource.heartbeat_utc
                $stepsCompleted = @($postrun.steps).Count
            }
            [pscustomobject]@{
                observer_status = 'VERIFIED_ORIGINAL_PROCESS_HANDLE_LIVE'
                verified_pid = $controllerPid
                controller_started = $controllerStarted
                completed = $beat.completed
                planned = $beat.planned
                heartbeat_utc = $beat.utc
                final_disposition = $final
                observer_cpu_seconds = $observerProcess.TotalProcessorTime.TotalSeconds
                observer_affinity = 1
                postrun_steps_completed = $stepsCompleted
            } | ConvertTo-Json -Compress
            if ($final -and -not $FollowPostrun) { break }
        } catch {
            [pscustomobject]@{ observer_status = 'HEARTBEAT_OBSERVATION_INCOMPLETE'; original_handle_exited = $controllerProcess.HasExited } | ConvertTo-Json -Compress
        }
        $remainingMilliseconds = $IntervalSeconds * 1000
        while ($remainingMilliseconds -gt 0) {
            $sliceMilliseconds = [Math]::Min(45000, $remainingMilliseconds)
            if ($controllerProcess.WaitForExit($sliceMilliseconds)) { break }
            $remainingMilliseconds -= $sliceMilliseconds
        }
    }
    [pscustomobject]@{ observer_status = 'OBSERVATION_WINDOW_ENDED'; controller_exited = $controllerProcess.HasExited; model_stop_requested = $false } | ConvertTo-Json -Compress
} finally {
    $controllerProcess.Dispose()
    $observerProcess.Dispose()
}
