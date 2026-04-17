#!/usr/bin/env python
"""
Batch processing utility for FrankenBlast

Process multiple transients from a CSV file or list.
"""

import os
import sys
import csv
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import traceback

from frankenblast import FrankenBlast

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BatchProcessor')


class BatchProcessor:
    """Batch processing for multiple transients"""
    
    def __init__(self, input_file: str, output_dir: str = "batch_results",
                 max_workers: int = 1):
        """
        Initialize batch processor.
        
        Parameters
        ----------
        input_file : str
            Path to CSV file with transient list
        output_dir : str
            Directory for output files
        max_workers : int
            Number of parallel workers
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup batch log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.batch_log = self.output_dir / f"batch_log_{timestamp}.json"
        self.results = []
        
    def load_transients(self) -> List[Dict]:
        """
        Load transient list from CSV file.
        
        Expected columns: name, ra, dec, redshift (optional)
        
        Returns
        -------
        list
            List of transient dictionaries
        """
        transients = []
        
        with open(self.input_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                transient = {
                    'name': row['name'],
                    'ra': float(row['ra']),
                    'dec': float(row['dec']),
                    'redshift': float(row['redshift']) if row.get('redshift') and row['redshift'] else None
                }
                transients.append(transient)
        
        logger.info(f"Loaded {len(transients)} transients from {self.input_file}")
        return transients
    
    def process_single(self, transient: Dict, pipeline_steps: List[str],
                      kwargs: Optional[Dict] = None) -> Dict:
        """
        Process a single transient.
        
        Parameters
        ----------
        transient : dict
            Transient information
        pipeline_steps : list
            List of steps to run: ['host', 'photometry', 'sed']
        kwargs : dict, optional
            Additional arguments for pipeline steps
            
        Returns
        -------
        dict
            Processing results
        """
        if kwargs is None:
            kwargs = {}
        
        result = {
            'name': transient['name'],
            'ra': transient['ra'],
            'dec': transient['dec'],
            'redshift': transient.get('redshift'),
            'success': False,
            'error': None,
            'steps_completed': []
        }
        
        try:
            # Initialize FrankenBlast
            fb = FrankenBlast(
                transient['name'],
                transient['ra'],
                transient['dec'],
                transient.get('redshift')
            )
            
            # Create transient-specific output directory
            transient_dir = self.output_dir / transient['name']
            transient_dir.mkdir(exist_ok=True)
            
            # Run requested pipeline steps
            if 'host' in pipeline_steps:
                logger.info(f"Finding host for {transient['name']}...")
                host_kwargs = kwargs.get('host', {})
                host_kwargs['output_dir'] = str(transient_dir)
                host_info = fb.find_host(**host_kwargs)
                
                result['host_found'] = host_info['host_ra'] is not None
                if result['host_found']:
                    result['host_ra'] = host_info['host_ra']
                    result['host_dec'] = host_info['host_dec']
                    result['host_redshift'] = host_info['host_redshift_mean']
                    result['host_probability'] = host_info['host_prob']
                result['steps_completed'].append('host')
                
                if not result['host_found'] and ('photometry' in pipeline_steps or 'sed' in pipeline_steps):
                    logger.warning(f"No host found for {transient['name']}, skipping photometry/SED")
                    result['error'] = "No host found"
                    return result
            
            if 'photometry' in pipeline_steps:
                logger.info(f"Running photometry for {transient['name']}...")
                phot_kwargs = kwargs.get('photometry', {})
                phot_kwargs['output_file'] = str(transient_dir / f"{transient['name']}_photometry.json")
                phot_kwargs['save_results'] = True
                
                fb.download_images()
                photometry = fb.do_photometry(**phot_kwargs)
                
                result['n_photometry'] = sum(1 for f in photometry['filters'] if f['flux_mJy'] is not None)
                result['n_filters'] = len(photometry['filters'])
                result['steps_completed'].append('photometry')
            
            if 'sed' in pipeline_steps:
                logger.info(f"Running SED fitting for {transient['name']}...")
                sed_kwargs = kwargs.get('sed', {})
                sed_result = fb.fit_sed(**sed_kwargs)
                
                result['sed_status'] = sed_result
                result['steps_completed'].append('sed')
            
            result['success'] = True
            logger.info(f"Successfully processed {transient['name']}")
            
        except Exception as e:
            logger.error(f"Error processing {transient['name']}: {e}")
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
        
        return result
    
    def run_batch(self, pipeline_steps: List[str] = None,
                 kwargs: Optional[Dict] = None,
                 parallel: bool = False) -> List[Dict]:
        """
        Run batch processing on all transients.
        
        Parameters
        ----------
        pipeline_steps : list, optional
            Steps to run. Default: ['host', 'photometry', 'sed']
        kwargs : dict, optional
            Additional arguments for pipeline steps
        parallel : bool
            Run in parallel (use with caution)
            
        Returns
        -------
        list
            List of processing results
        """
        if pipeline_steps is None:
            pipeline_steps = ['host', 'photometry', 'sed']
        
        # Load transients
        transients = self.load_transients()
        
        logger.info(f"Starting batch processing for {len(transients)} transients")
        logger.info(f"Pipeline steps: {pipeline_steps}")
        
        if parallel and self.max_workers > 1:
            # Parallel processing
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_single, t, pipeline_steps, kwargs): t
                    for t in transients
                }
                
                for future in as_completed(futures):
                    transient = futures[future]
                    try:
                        result = future.result()
                        self.results.append(result)
                        self.save_progress()
                    except Exception as e:
                        logger.error(f"Failed to process {transient['name']}: {e}")
                        self.results.append({
                            'name': transient['name'],
                            'success': False,
                            'error': str(e)
                        })
        else:
            # Sequential processing
            for i, transient in enumerate(transients, 1):
                logger.info(f"Processing {i}/{len(transients)}: {transient['name']}")
                result = self.process_single(transient, pipeline_steps, kwargs)
                self.results.append(result)
                self.save_progress()
        
        # Save final results
        self.save_summary()
        
        # Print summary
        successful = sum(1 for r in self.results if r['success'])
        logger.info(f"\nBatch processing complete!")
        logger.info(f"Successfully processed: {successful}/{len(transients)}")
        
        return self.results
    
    def save_progress(self):
        """Save current progress to log file"""
        with open(self.batch_log, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def save_summary(self):
        """Save summary CSV file"""
        summary_file = self.output_dir / "batch_summary.csv"
        
        # Convert results to DataFrame
        df = pd.DataFrame(self.results)
        df.to_csv(summary_file, index=False)
        
        logger.info(f"Saved summary to {summary_file}")
        
        # Create detailed report
        report_file = self.output_dir / "batch_report.txt"
        with open(report_file, 'w') as f:
            f.write("FrankenBlast Batch Processing Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total transients: {len(self.results)}\n")
            f.write(f"Successful: {sum(1 for r in self.results if r['success'])}\n")
            f.write(f"Failed: {sum(1 for r in self.results if not r['success'])}\n\n")
            
            # Success details
            f.write("Successful Processing:\n")
            f.write("-" * 30 + "\n")
            for r in self.results:
                if r['success']:
                    f.write(f"  {r['name']}: {', '.join(r['steps_completed'])}\n")
            
            # Failure details
            f.write("\nFailed Processing:\n")
            f.write("-" * 30 + "\n")
            for r in self.results:
                if not r['success']:
                    f.write(f"  {r['name']}: {r.get('error', 'Unknown error')}\n")
        
        logger.info(f"Saved report to {report_file}")


def main():
    """Command line interface for batch processing"""
    parser = argparse.ArgumentParser(
        description='Batch process multiple transients with FrankenBlast'
    )
    
    parser.add_argument('input_file', type=str,
                       help='CSV file with transient list (columns: name, ra, dec, [redshift])')
    parser.add_argument('--output-dir', type=str, default='batch_results',
                       help='Output directory for results')
    parser.add_argument('--steps', nargs='+', 
                       choices=['host', 'photometry', 'sed'],
                       default=['host', 'photometry', 'sed'],
                       help='Pipeline steps to run')
    parser.add_argument('--config', type=str,
                       help='Configuration file with additional parameters')
    parser.add_argument('--parallel', action='store_true',
                       help='Run in parallel (use with caution)')
    parser.add_argument('--max-workers', type=int, default=2,
                       help='Maximum number of parallel workers')
    
    args = parser.parse_args()
    
    # Load configuration if provided
    kwargs = {}
    if args.config:
        with open(args.config, 'r') as f:
            if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                import yaml
                kwargs = yaml.safe_load(f)
            else:
                kwargs = json.load(f)
    
    # Create batch processor
    processor = BatchProcessor(
        args.input_file,
        args.output_dir,
        args.max_workers
    )
    
    # Run batch processing
    results = processor.run_batch(
        pipeline_steps=args.steps,
        kwargs=kwargs,
        parallel=args.parallel
    )
    
    # Print final summary
    successful = sum(1 for r in results if r['success'])
    print(f"\nProcessing complete: {successful}/{len(results)} successful")


if __name__ == '__main__':
    main()