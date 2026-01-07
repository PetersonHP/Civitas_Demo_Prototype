#!/usr/bin/env python3
"""
Analyze dispatcher test results from JSONL file.
Calculates accuracy and average elapsed time, then generates a scatterplot.
"""

import json
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def analyze_results(jsonl_file):
    """Analyze test results from JSONL file."""
    total_count = 0
    correct_count = 0
    elapsed_times = []
    results = []
    filtered_results = []
    filtered_correct_count = 0

    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                total_count += 1

                is_correct = data.get('is_correct', False)
                elapsed_time = data.get('elapsed_time_seconds', 0)

                if is_correct:
                    correct_count += 1

                elapsed_times.append(elapsed_time)
                result = {
                    'index': total_count,
                    'is_correct': is_correct,
                    'elapsed_time': elapsed_time,
                    'ticket_id': data.get('ticket_id', 'unknown'),
                    'unique_key': data.get('unique_key', 'unknown')
                }
                results.append(result)

                # Filter out outliers over 300s
                if elapsed_time <= 300:
                    filtered_results.append(result)
                    if is_correct:
                        filtered_correct_count += 1

    # Calculate metrics using filtered data only
    filtered_count = len(filtered_results)
    accuracy = (filtered_correct_count / filtered_count * 100) if filtered_count > 0 else 0

    filtered_times = [r['elapsed_time'] for r in filtered_results]
    avg_elapsed_time = sum(filtered_times) / len(filtered_times) if filtered_times else 0

    # Calculate metrics for non-rate-limited requests (< 25s)
    non_rate_limited_results = [r for r in filtered_results if r['elapsed_time'] < 25]
    non_rate_limited_times = [r['elapsed_time'] for r in non_rate_limited_results]
    non_rate_limited_correct = sum(1 for r in non_rate_limited_results if r['is_correct'])
    non_rate_limited_count = len(non_rate_limited_results)

    avg_non_rate_limited_time = (
        sum(non_rate_limited_times) / len(non_rate_limited_times)
        if non_rate_limited_times else 0
    )

    non_rate_limited_accuracy = (
        (non_rate_limited_correct / non_rate_limited_count * 100)
        if non_rate_limited_count > 0 else 0
    )

    return {
        'total': total_count,
        'correct': correct_count,
        'filtered_total': filtered_count,
        'filtered_correct': filtered_correct_count,
        'accuracy': accuracy,
        'avg_elapsed_time': avg_elapsed_time,
        'avg_non_rate_limited_time': avg_non_rate_limited_time,
        'non_rate_limited_count': non_rate_limited_count,
        'non_rate_limited_correct': non_rate_limited_correct,
        'non_rate_limited_accuracy': non_rate_limited_accuracy,
        'results': results
    }


def create_scatterplot(analysis, output_dir):
    """Create a bell curve distribution of test results showing elapsed time distribution."""
    results = analysis['results']

    # Create figure
    plt.figure(figsize=(12, 6))

    # Prepare data for histogram
    all_times = [r['elapsed_time'] for r in results]

    # Determine bin range and count
    if all_times:
        bins = 1000  # Number of bins for the histogram

        # Plot single histogram
        plt.hist(
            all_times,
            bins=bins,
            color='blue',
            alpha=0.7,
            label=f'All Results (n={len(all_times)})',
            edgecolor='darkblue',
            linewidth=1.5,
            density=True
        )

    # Add labels and title
    plt.xlabel('Elapsed Time (seconds)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.xlim(0, 110)  # Limit x-axis to 0-110 seconds
    plt.title(
        'Dispatcher Test Results - Elapsed Time Distribution\n',
        # f'Accuracy: {analysis["accuracy"]:.1f}% ({analysis["filtered_correct"]}/{analysis["filtered_total"]}) | '
        # f'Avg Time: {analysis["avg_elapsed_time"]:.2f}s | '
        # f'Avg Time (<25s): {analysis["avg_non_rate_limited_time"]:.2f}s',
        fontsize=14,
        fontweight='bold'
    )
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    # Save plot
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'test_results_histogram.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Histogram saved to: {output_file}")

    plt.close()


def create_scatterplot_dots(analysis, output_dir):
    """Create a scatterplot with color-coded dots for correct (green) and incorrect (red) results."""
    results = analysis['results']

    # Create figure
    plt.figure(figsize=(12, 6))

    # Separate correct and incorrect results
    correct_results = [r for r in results if r['is_correct']]
    incorrect_results = [r for r in results if not r['is_correct']]

    # Plot correct results (green)
    if correct_results:
        correct_indices = [r['index'] for r in correct_results]
        correct_times = [r['elapsed_time'] for r in correct_results]
        plt.scatter(
            correct_indices,
            correct_times,
            color='green',
            alpha=0.6,
            s=50,
            label=f'Correct (n={len(correct_results)})',
            edgecolors='darkgreen',
            linewidths=0.5
        )

    # Plot incorrect results (red)
    if incorrect_results:
        incorrect_indices = [r['index'] for r in incorrect_results]
        incorrect_times = [r['elapsed_time'] for r in incorrect_results]
        plt.scatter(
            incorrect_indices,
            incorrect_times,
            color='red',
            alpha=0.6,
            s=50,
            label=f'Incorrect (n={len(incorrect_results)})',
            edgecolors='darkred',
            linewidths=0.5
        )

    # Add labels and title
    plt.xlabel('Test Case Index', fontsize=12)
    plt.ylabel('Elapsed Time (seconds)', fontsize=12)
    plt.ylim(0, 110)  # Limit y-axis to 0-110 seconds
    plt.title(
        'Dispatcher Test Results - Scatterplot\n',
        fontsize=14,
        fontweight='bold'
    )
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Save plot
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'test_results_scatterplot.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Scatterplot saved to: {output_file}")

    plt.close()


def create_comparison_histograms(analysis, output_dir):
    """Create side-by-side histograms comparing correct and incorrect result distributions."""
    results = analysis['results']

    # Separate correct and incorrect results
    correct_times = [r['elapsed_time'] for r in results if r['is_correct']]
    incorrect_times = [r['elapsed_time'] for r in results if not r['is_correct']]

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    bins = 50  # Number of bins for both histograms

    # Left subplot: Correct results (green)
    if correct_times:
        ax1.hist(
            correct_times,
            bins=500,
            color='green',
            alpha=0.7,
            edgecolor='darkgreen',
            linewidth=1.5,
            density=True
        )
        ax1.set_xlabel('Elapsed Time (seconds)', fontsize=12)
        ax1.set_ylabel('Density', fontsize=12)
        ax1.set_xlim(0, 110)
        ax1.set_title(
            f'Correct Results (n={len(correct_times)})\n'
            f'Mean: {sum(correct_times)/len(correct_times):.2f}s',
            fontsize=13,
            fontweight='bold',
            color='darkgreen'
        )
        ax1.grid(True, alpha=0.3, axis='y')

    # Right subplot: Incorrect results (red)
    if incorrect_times:
        ax2.hist(
            incorrect_times,
            bins=bins,
            color='red',
            alpha=0.7,
            edgecolor='darkred',
            linewidth=1.5,
            density=True
        )
        ax2.set_xlabel('Elapsed Time (seconds)', fontsize=12)
        ax2.set_ylabel('Density', fontsize=12)
        ax2.set_xlim(0, 110)
        ax2.set_title(
            f'Incorrect Results (n={len(incorrect_times)})\n'
            f'Mean: {sum(incorrect_times)/len(incorrect_times):.2f}s',
            fontsize=13,
            fontweight='bold',
            color='darkred'
        )
        ax2.grid(True, alpha=0.3, axis='y')

    # Overall title
    fig.suptitle(
        'Distribution Comparison: Correct vs Incorrect',
        fontsize=16,
        fontweight='bold',
        y=1.00
    )

    plt.tight_layout()

    # Save plot
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'test_results_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Comparison histogram saved to: {output_file}")

    plt.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_test_results.py <jsonl_file>")
        sys.exit(1)

    jsonl_file = sys.argv[1]

    if not os.path.exists(jsonl_file):
        print(f"Error: File not found: {jsonl_file}")
        sys.exit(1)

    # Analyze results
    print(f"Analyzing results from: {jsonl_file}")
    analysis = analyze_results(jsonl_file)

    # Print summary
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY (excluding >300s outliers)")
    print("="*50)
    print(f"Total test cases (raw): {analysis['total']}")
    print(f"Test cases analyzed: {analysis['filtered_total']} (excluded {analysis['total'] - analysis['filtered_total']} outliers)")
    print(f"Correct assignments: {analysis['filtered_correct']}")
    print(f"Incorrect assignments: {analysis['filtered_total'] - analysis['filtered_correct']}")
    print(f"Accuracy: {analysis['accuracy']:.2f}%")
    print(f"Average elapsed time: {analysis['avg_elapsed_time']:.2f} seconds")
    print()
    print("Under 25s Sample (non-rate-limited):")
    print(f"  Count: {analysis['non_rate_limited_count']}/{analysis['filtered_total']}")
    print(f"  Correct: {analysis['non_rate_limited_correct']}")
    print(f"  Incorrect: {analysis['non_rate_limited_count'] - analysis['non_rate_limited_correct']}")
    print(f"  Accuracy: {analysis['non_rate_limited_accuracy']:.2f}%")
    print(f"  Average elapsed time: {analysis['avg_non_rate_limited_time']:.2f} seconds")
    print("="*50 + "\n")

    # Create plots
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir / 'logs' / 'test_results'
    create_scatterplot(analysis, output_dir)
    create_scatterplot_dots(analysis, output_dir)
    create_comparison_histograms(analysis, output_dir)


if __name__ == '__main__':
    main()
