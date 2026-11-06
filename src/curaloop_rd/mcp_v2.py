"""The pinned v1 stdio transport with additive, versioned EN/TH export views."""
import argparse
from pathlib import Path
import sys
from .mcp_v1 import serve
from .portfolio_v2 import Portfolio

def main():
    parser=argparse.ArgumentParser()
    for name in ['source-root','registry','workspace','font']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    portfolio=Portfolio(args.source_root,args.registry,args.workspace,args.font)
    try:serve(portfolio,sys.stdin.buffer,sys.stdout)
    finally:portfolio.close()

if __name__=='__main__':main()
