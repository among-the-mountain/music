#!/usr/bin/env python3
"""
Main runner script for Yambda Music Analysis System
Executes all modules in sequence
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error: {description} failed")
        sys.exit(1)
    
    print(f"✓ {description} completed successfully")

def main():
    """Main execution flow"""
    print("\n" + "="*60)
    print("Yambda Music Behavior Analysis & ML System")
    print("="*60)
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Step 1: Data preprocessing
    run_command(
        'python scripts/data_loader.py',
        'MODULE 0 & 1: Data Loading and Preprocessing'
    )
    
    # Step 2: Machine learning modules
    run_command(
        'python scripts/ml_modules.py',
        'MODULE 2, 3 & 4: Machine Learning Training'
    )
    
    print("\n" + "="*60)
    print("All modules completed successfully!")
    print("="*60)
    print("\nTo start the dashboard:")
    print("  python app.py")
    print("\nThen open your browser to: http://localhost:5000")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
