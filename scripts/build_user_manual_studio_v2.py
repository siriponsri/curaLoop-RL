"""Versioned English manual from unchanged actual browser captures."""
from pathlib import Path
import argparse,hashlib,json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader

PAGES=[
 ('Molecular Studio','01-overview-en.png','Inspect before requesting',[
  'Open Start-CuraLoop-Web.cmd on Windows, then use the local address shown by the launcher. Installation requires the documented dependencies; the application runs on CPU.',
  'The overview presents an eligible historical compound and its public structure. Use Previous compound, Next compound and the zoom controls. Previewing does not request an assay.',
  'The sidebar opens the seven work areas. EN and Thai switch interface language while retaining the active campaign. Source quotations and original diagnostics retain their original language.']),
 ('Configure a campaign','02-scenario-en.png','Make the constraints explicit',[
  'Open Scenario builder. Choose historical HIV replay or a labelled synthetic fixture, then select an acquisition policy.',
  'Set seed, screening budget, initial labels, concurrent assay capacity, feedback delay and cost per assay. Expand additional settings for jitter and missingness.',
  'Create campaign starts an independent campaign. For the illustrated short walkthrough, budget 6, capacity 2 and delay 2 are simulated constraints, not laboratory costs or elapsed hours.']),
 ('Request and wait','03-lab-pending-en.png','Pending is not delivered',[
  'In Simulation lab, Select next batch requests the next eligible candidates. Accepted requests reserve budget once.',
  'Review candidate identities and due steps in Feedback queue. Outcome labels stay hidden while requests are pending. Confirmed new hits exclude seed labels and predictions.',
  'When selection is unavailable and requests are pending, Advance +1 step is the primary action. It advances simulated time; it does not perform a real assay.']),
 ('Read delivered results','03-lab-delivered-en.png','Follow the event ledger',[
  'Advance +1 step until a request is due. The illustrated delay 2 campaign delivers its first two requests after two explicit advances.',
  'Read delivered, missing and confirmed-hit counts separately. The decision table retains selection explanations and original model status. The event ledger records accepted actions.',
  'Complete run explicitly finishes the simulation. Verify replay reconciles the public event history. Reset creates a fresh run; export JSON first when retaining a portable recovery copy.']),
 ('Explore compounds','04-compounds-en.png','Inspect the public record',[
  'Use Compound explorer to search, filter and sort candidates. Filters distinguish eligible, pending and observed records without revealing hidden outcomes.',
  'Select a compound to open its details. Historical molecules use genuine RDKit-rendered structures; synthetic fixtures may have descriptors without a molecular structure.',
  'Close the dialog with Escape to return focus to the selected compound. Public structures are not evidence that a compound is effective or safe.']),
 ('Compare policies','05-benchmarks-en.png','Use matched conditions',[
  'Benchmark arena starts independent campaigns with the same scenario and seed labels. Select policies, then Compare selected policies.',
  'Wait for the actual job to complete. Reopen completed comparisons through saved history. Interrupted jobs remain interrupted and are not automatically replayed.',
  'Export the comparison JSON or CSV. A comparison is not a single-run recovery file. Historical recorded benchmark summaries remain distinct from the current job.']),
 ('Export and recover','06-evidence-en.png','Preserve the campaign',[
  'Research evidence explains provenance, model fallback and scientific limitations. JSON contains a portable single-run public snapshot; CSV is an event ledger.',
  'To recover, choose that JSON under Your evidence travels with you and select Validate & resume. Validation creates an independent recovered campaign. Open Simulation lab to continue its pending queue.',
  'Saved campaigns and revisions can be reopened or recovered without overwriting the original. If an action fails, retain the current state, read the original diagnostic and retry explicitly after resolving the issue.']),
 ('Present the work','07-guide-en.png','Keep the evidence visible',[
  'Guided presentation supports a short explanation of the screening loop using the current campaign.',
  'Separate source observations, simulated operations and policy predictions. Do not describe historical replay as a prospective laboratory experiment.',
  'Research evidence contains reproducibility details and source limitations. Build identities belong with that evidence rather than the normal task interface.']),
 ('Trace metadata','08-workspace-en.png','Follow a field to its source',[
  'Open the C Workspace HTML in the exported view-v2 folder, or the linked repository demo. Select a declared field to update its raw value and source locator together.',
  'Expand Inspect citation to read the original registry identity, locator and available hashes. On mobile, rows stack so complete references remain accessible.',
  'Raw unit and value-type codes are preserved. No conversion is implied. The displayed readout is cached provider metadata, not a molecular activity result.']),
 ('Plan and hand off','08-workspace-en.png','Understand the release boundary',[
  'Readiness plan lists metadata review and endpoint/population qualification. Expand Scope and limits before considering any molecular experiment.',
  'Portable files include the report, readiness plan, preview receipt and handoff manifest. Downloading a local file does not deliver it to a team tool.',
  'The frozen report identity is retained by the new bilingual view. Molecular replay remains unmet, live-agent efficacy is untested and commercial provider-data clearance is not established.']),
 ('Language and access','01-overview-en.png','One state, two interfaces',[
  'EN and Thai persist as a browser preference. Switching language does not create a new campaign, advance time, request assays or change raw source values.',
  'Use keyboard focus and native controls. Reduced-motion preference suppresses the runtime heading transition. Scientific chart values do not animate.',
  'Desktop 1440x1000, mobile 390x844 and 720px reflow were inspected. These are emulated viewports, not real-device qualification. Native browser 200% zoom and other browser engines were not verified.']),
 ('Scope and next checkpoint',None,'Research POC, with limits',[
  'The frontend checkpoint covers the bilingual main application, additive C Workspace, actual browser captures, local exports and this English manual.',
  'The separate 20-second HyperFrames walkthrough animates actual captures. It is not a continuous live recording, a real-agent evaluation or proof of scientific benefit.',
  'The owner requested a pause after frontend delivery. Research resumes only after owner resume. Final outcomes, source STOPs and previous scientific NO_GO decisions remain unchanged.'])]

def build(captures,output):
 output.parent.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(output),pagesize=(842,595),pageCompression=1)
 c.setTitle('CuraLoop-RL | Molecular Studio - English User Manual')
 c.setAuthor('CuraLoop-RL project')
 style=ParagraphStyle('body',fontName='Helvetica',fontSize=10.2,leading=15,textColor=colors.HexColor('#28282B'),spaceAfter=10)
 pins=[]
 for number,(title,image,sub,paragraphs) in enumerate(PAGES,1):
  c.setFillColor(colors.HexColor('#F6F4EF'));c.rect(0,0,842,595,fill=1,stroke=0)
  c.setFillColor(colors.HexColor('#A6492D'));c.setFont('Helvetica-Bold',10);c.drawString(30,565,'CURALOOP-RL  /  MOLECULAR STUDIO  /  ENGLISH MANUAL')
  c.setFillColor(colors.HexColor('#28282B'));c.setFont('Helvetica-Bold',25);c.drawString(30,526,title)
  c.setFont('Helvetica',11);c.setFillColor(colors.HexColor('#6A6661'));c.drawString(30,504,sub)
  if image:
   p=captures/image;raw=p.read_bytes();pins.append({'path':image,'sha256':hashlib.sha256(raw).hexdigest()})
   reader=ImageReader(str(p));iw,ih=reader.getSize();x,y,w,h=30,58,553,423
   c.setFillColor(colors.white);c.rect(x,y,w,h,fill=1,stroke=0)
   c.saveState();clip=c.beginPath();clip.rect(x,y,w,h);c.clipPath(clip,stroke=0,fill=0)
   height=ih*w/iw;c.drawImage(reader,x,y+h-height,width=w,height=height);c.restoreState()
   c.setStrokeColor(colors.HexColor('#D9D5CF'));c.rect(x,y,w,h,fill=0,stroke=1)
   tx,tw,ty=605,207,477
  else:tx,tw,ty=50,710,465
  for i,text in enumerate(paragraphs,1):
   para=Paragraph(f'<b>{i:02d}</b>  '+text,style);pw,ph=para.wrap(tw,450);assert ty-ph>48,(number,ty,ph)
   para.drawOn(c,tx,ty-ph);ty-=ph+19
  c.setFillColor(colors.HexColor('#6A6661'));c.setFont('Helvetica',8)
  c.drawString(30,26,'6 November 2026 | Actual captures; figures show the upper viewport where cropped. Full PNGs accompany the evidence packet.')
  c.drawRightString(812,26,f'{number:02d} / {len(PAGES):02d}');c.showPage()
 c.save()
 reader=PdfReader(output);assert len(reader.pages)==len(PAGES)
 assert all(page.extract_text().strip() for page in reader.pages)
 result={'status':'PASS_CREATED_AND_TEXT_REOPENED','pages':len(reader.pages),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'capture_pins':pins,'visual_check':'PENDING_RENDER_INSPECTION'}
 output.with_suffix('.validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','pages','sha256']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();build(args.captures,args.output)
