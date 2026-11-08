"""Final-size scientific figures from verified aggregate evidence, never raw labels."""
import hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.m2_costed_v2.guard import CostedGuard,new
TASK=ROOT/'.local/m2-costed-20261108-v2';PUBLIC=ROOT/'docs/evidence/m2-costed-20261108-v2'
SKILL=Path('C:/Users/User/.codex/plugins/cache/openai-curated-remote/scientific-visual-table-style/2.2.0/skills/scientific-visual-table-style')
ARMS=['R','G1','Gk','U','P','T','E','L'];FOCAL='#9C5B36';INK='#242424';GRAY='#656565'


def main():
    permit=json.loads((TASK/'jobs/figures-v1/permit.json').read_text());job=TASK/'jobs'/permit['attempt'];guard=CostedGuard(job/'resource.json',permit)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        from PIL import Image,ImageOps
        from matplotlib.text import Text
        from matplotlib.ticker import MaxNLocator
        assert json.loads((TASK/'jobs/analysis-v1/result.json').read_text())['status']=='PASS_COMPLETE_MATRIX_ANALYSIS'
        data=json.loads((PUBLIC/'aggregate-results-v1.json').read_text())
        curves={r['arm']:r for r in data['discovery_curves'] if r['predictor']=='rf' and r['regime']=='cheap'};assert set(curves)==set(ARMS)
        effects=[r for r in data['paired_contrasts'] if r['predictor']=='rf' and r['regime']=='cheap']
        extraction={'curves':curves,'effects':effects};checksum=hashlib.sha256(json.dumps(extraction,sort_keys=True).encode()).hexdigest()
        new(PUBLIC/'figure-data-v1.json',extraction)
        spec={'claim':'Compare absolute discovery and paired differences without promoting exposed development evidence to confirmation.',
          'audience':'expert','visual_form':'small_multiples','metric':{'name':'Newly delivered assay-relative binary positives','unit':'count',
          'direction':'higher','aggregation':'seeds/n0 within assay; assays within component; four components equal','denominator':'assigned B=32','precision_decimals':2},
          'data_source':{'path_or_identifier':'figure-data-v1.json','checksum':checksum,'immutable_fields':['curves','effects']},
          'focal_series':'L','required_baselines':ARMS[:-1],'series_order':ARMS,'ordering_rationale':'predefined_benchmark',
          'uncertainty':{'available':True,'type':'bootstrap_interval','level':.95,'sample_or_seed_count':5,
          'note':'10,000 shared seed-index resamples; conditional on six exposed assays/four fixed annotation components'},
          'target':{'medium':'paper','width':178,'height':110,'unit':'mm','minimum_text_size_pt':8.5,'background':'white'},
          'selected_reference_ids':['OAI-VIS-004','OAI-VIS-011','OAI-VIS-013','OAI-VIS-014'],
          'output_formats':['svg','pdf','png'],'caption_requirements':['task','sample','estimator','uncertainty','exclusions','metric_direction'],
          'exceptions':[{'rule':'focal teal','reason':'Owner selected Graphite x Copper and rejected the earlier green/teal theme.'}]}
        new(TASK/'scientific-visual-spec-v1.json',spec)
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.labelsize':8.5,'axes.titlesize':9,
          'xtick.labelsize':8.5,'ytick.labelsize':8.5,'legend.fontsize':8.5,'text.color':INK,'axes.labelcolor':INK,
          'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#787878','axes.linewidth':.65,'figure.facecolor':'white',
          'axes.facecolor':'white','savefig.facecolor':'white','svg.fonttype':'none','pdf.fonttype':42,
          'lines.linewidth':1.1,'axes.spines.top':False,'axes.spines.right':False,'axes.unicode_minus':True})
        qa_spec=importlib.util.spec_from_file_location('m2_visual_preflight',SKILL/'scripts/visual_qa.py')
        qa=importlib.util.module_from_spec(qa_spec);sys.modules[qa_spec.name]=qa;qa_spec.loader.exec_module(qa)
        qa_rows=[];bounds=[];formats=[]
        def save(fig,name,height):
            fig.canvas.draw();renderer=fig.canvas.get_renderer();canvas=fig.bbox
            for text in fig.findobj(Text):
                if not text.get_visible() or not text.get_text().strip():continue
                assert text.get_fontsize()>=8.49,(name,text.get_text(),'FONT_TOO_SMALL')
                box=text.get_window_extent(renderer)
                assert box.x0>=canvas.x0-1 and box.x1<=canvas.x1+1 and box.y0>=canvas.y0-1 and box.y1<=canvas.y1+1,(name,text.get_text(),'CLIPPED_TEXT')
            bounds.append({'name':name,'status':'PASS_TEXT_SIZE_AND_CANVAS_BOUNDS','width_mm':178,'height_mm':height,'minimum_font_pt':8.5})
            for ext in('svg','pdf','png'):
                path=PUBLIC/(name+'.'+ext);assert not path.exists()
                fig.savefig(path,dpi=300,format=ext)
                report=qa.inspect_visual(path,target_width_mm=178,target_height_mm=height,min_font_pt=8.5).to_dict()
                qa_rows.append(report);assert report['passed'],report
                formats.append(str(path.relative_to(ROOT)).replace('\\','/'))
            with Image.open(PUBLIC/(name+'.png')) as raster:
                ImageOps.grayscale(raster).save(TASK/(name+'-grayscale.png'))
            plt.close(fig)
        fig,axes=plt.subplots(1,2,figsize=(178/25.4,110/25.4),gridspec_kw={'width_ratios':[1,1.1]})
        fig.subplots_adjust(left=.09,right=.975,bottom=.23,top=.77,wspace=.40)
        fig.text(.025,.96,'RF discovery under a fixed computation budget',fontsize=10,weight='semibold',va='top')
        fig.text(.025,.89,'Six exposed assays / four annotation components / five paired seeds',fontsize=8.5,va='top')
        ax=axes[0]
        for i,arm in enumerate(ARMS):
            c=curves[arm];mean=c['mean_new_positives'][-1];lo=c['conditional_seed_lower_95'][-1];hi=c['conditional_seed_upper_95'][-1]
            ax.hlines(i,lo,hi,color=FOCAL if arm=='L' else GRAY,lw=.9)
            ax.scatter(mean,i,s=23 if arm=='L' else 18,color=FOCAL if arm=='L' else GRAY,marker='D' if arm=='L' else 'o',zorder=3)
        ax.set_yticks(range(8),ARMS);ax.invert_yaxis();ax.set_xlim(0,32);ax.set_xticks([0,8,16,24,32]);ax.set_xlabel('New binary positives (B = 32)')
        ax.set_title('(a) Absolute discovery',loc='left',pad=9)
        ax=axes[1]
        extent=max(1,max(abs(x) for r in effects for x in r['conditional_seed_interval_95']))*1.15
        for i,r in enumerate(effects):
            lo,hi=r['conditional_seed_interval_95'];ax.hlines(i,lo,hi,color=FOCAL,lw=.9);ax.scatter(r['mean_delta_new_positives'],i,s=23,color=FOCAL,marker='D',zorder=3)
        ax.axvline(0,color='#B2B2B2',lw=.75);ax.set_yticks(range(3),[r['contrast'].replace('-',' − ') for r in effects]);ax.invert_yaxis()
        ax.set_xlim(-extent,extent);ax.xaxis.set_major_locator(MaxNLocator(5,prune='both'));ax.set_xlabel('Change in new positives')
        ax.set_title('(b) Paired primary contrasts',loc='left',pad=9)
        fig.text(.025,.11,'RF / Ccheap / n0 = 0 or 16. Initial positives excluded.',fontsize=8.5)
        fig.text(.025,.055,'Whiskers: 95% conditional seed intervals, not family-population intervals.',fontsize=8.5)
        save(fig,'primary-discovery-v1',110)
        for index,subset in enumerate((ARMS[:4],ARMS[4:]),1):
            fig,axes=plt.subplots(2,2,figsize=(178/25.4,145/25.4),sharex=True,sharey=True)
            fig.subplots_adjust(left=.105,right=.975,bottom=.23,top=.78,hspace=.40,wspace=.23)
            fig.text(.025,.96,f'RF discovery curves: comparisons {index} of 2',fontsize=10,weight='semibold',va='top')
            fig.text(.025,.90,'Component-balanced means / B = 32 / Ccheap / n0 = 0 or 16',fontsize=8.5,va='top')
            for ax,arm in zip(axes.flat,subset):
                for current in ([arm,'L'] if arm!='L' else ['L']):
                    c=curves[current];color=FOCAL if current=='L' else GRAY
                    ax.fill_between(c['query_budget'],c['conditional_seed_lower_95'],c['conditional_seed_upper_95'],color=color,alpha=.10,linewidth=0)
                    ax.plot(c['query_budget'],c['mean_new_positives'],color=color,lw=1.6 if current=='L' else 1.1,
                      linestyle='-' if current=='L' else '--',label='L: learned gate' if current=='L' else 'Comparator')
                ax.set_title(arm,loc='left',pad=5,color=FOCAL if arm=='L' else INK)
                ax.set_xlim(0,32);ax.set_ylim(0,32);ax.set_xticks([0,16,32]);ax.set_yticks([0,16,32])
                ax.grid(axis='y',color='#E8E8E5',lw=.5)
            handles,labels=axes.flat[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.08,.855),ncol=2,frameon=False)
            fig.supylabel('New binary positives',x=.02,fontsize=8.5);fig.supxlabel('Assigned query budget',y=.15,fontsize=8.5)
            fig.text(.025,.09,'Bands: 95% conditional seed intervals on the fixed exposed cohort.',fontsize=8.5)
            fig.text(.025,.045,'CPU-exhausted curves carry the last count forward; no free queries.',fontsize=8.5)
            save(fig,'rf-cheap-discovery-curves-'+str(index)+'-v1',145)
        new(TASK/'figure-programmatic-qa-v1.json',{'status':'PASS_PROGRAMMATIC_FIGURE_QA_MANUAL_REVIEW_PENDING',
          'source_values_sha256':checksum,'text_bounds':bounds,'preflight':qa_rows,'outputs':formats,'grayscale_previews_private':True})
        new(job/'result.json',{'status':'PASS_FIGURE_RENDER_AND_PREFLIGHT','figures':3,'formats':formats,'manual_review_required':True})
        guard.finish('PASS');print(json.dumps({'status':'PASS_FIGURE_RENDER_AND_PREFLIGHT','figures':3,'manual_review_required':True}))
    except BaseException as e:
        new(job/'failure.json',{'type':type(e).__name__,'message':str(e)[:500]});guard.finish('FAIL');raise


if __name__=='__main__':main()
