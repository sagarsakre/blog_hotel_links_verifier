#!/usr/bin/env python3
"""
Generate HTML dashboard from verification results
Reads JSON summary files and creates a beautiful HTML monitoring page
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def load_verification_results(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load all *_summary.json files from the input directory
    
    Args:
        input_dir: Directory containing JSON summary files
        
    Returns:
        List of verification result dictionaries
    """
    results = []
    input_path = Path(input_dir)
    
    # Find all JSON summary files
    json_files = list(input_path.glob('*_summary.json'))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {json_file}: {e}", file=sys.stderr)
    
    # Sort by destination name
    results.sort(key=lambda x: x.get('destination', ''))
    
    return results


def generate_dashboard_html(results: List[Dict[str, Any]]) -> str:
    """
    Generate HTML dashboard from verification results
    
    Args:
        results: List of verification result dictionaries
        
    Returns:
        HTML string
    """
    # Calculate overall statistics
    total_destinations = len(results)
    total_hotels = sum(r.get('total_hotels', 0) for r in results)
    total_available = sum(r.get('available', 0) for r in results)
    total_unavailable = sum(r.get('unavailable', 0) for r in results)
    total_errors = sum(r.get('errors', 0) for r in results)
    
    healthy_destinations = sum(1 for r in results if r.get('status') == 'healthy')
    issues_destinations = total_destinations - healthy_destinations
    
    # Determine overall health status
    if total_unavailable == 0 and total_errors == 0:
        overall_status = 'healthy'
        overall_badge = '✓ All Systems Healthy'
        overall_color = '#10b981'
    elif total_unavailable + total_errors < 5:
        overall_status = 'warning'
        overall_badge = '⚠ Minor Issues Detected'
        overall_color = '#f59e0b'
    else:
        overall_status = 'critical'
        overall_badge = '✗ Critical Issues'
        overall_color = '#ef4444'
    
    # Get last update time
    if results:
        latest_timestamp = max(r.get('timestamp', '') for r in results)
        try:
            last_update = datetime.fromisoformat(latest_timestamp).strftime('%B %d, %Y at %I:%M %p UTC')
        except:
            last_update = 'Unknown'
    else:
        last_update = 'No data available'
    
    # Generate destination rows HTML
    destination_rows = []
    for result in results:
        destination = result.get('destination', 'Unknown')
        blog_url = result.get('blog_url', '')
        total = result.get('total_hotels', 0)
        available = result.get('available', 0)
        unavailable = result.get('unavailable', 0)
        errors = result.get('errors', 0)
        status = result.get('status', 'unknown')
        timestamp = result.get('timestamp', '')
        
        # Format timestamp
        try:
            check_time = datetime.fromisoformat(timestamp).strftime('%b %d, %I:%M %p')
        except:
            check_time = 'N/A'
        
        # Status badge
        if status == 'healthy':
            status_html = '<span class="badge badge-success">✓ Healthy</span>'
        else:
            status_html = f'<span class="badge badge-warning">⚠ {unavailable + errors} Issue(s)</span>'
        
        # Unavailable hotels detail
        unavailable_hotels = result.get('unavailable_hotels', [])
        if unavailable_hotels:
            unavailable_html = '<ul class="unavailable-list">'
            for hotel in unavailable_hotels:  # Show all unavailable hotels
                hotel_name = hotel.get('hotel_name', 'Unknown')
                unavailable_html += f'<li>{hotel_name}</li>'
            unavailable_html += '</ul>'
        else:
            unavailable_html = '<span class="text-muted">None</span>'
        
        row_html = f'''
        <tr>
            <td>
                <a href="{blog_url}" target="_blank" class="destination-link">{destination}</a>
            </td>
            <td class="text-center">{total}</td>
            <td class="text-center text-success">{available}</td>
            <td class="text-center">{unavailable + errors if (unavailable + errors) > 0 else '-'}</td>
            <td class="text-center">{status_html}</td>
            <td class="text-center text-muted">{check_time}</td>
        </tr>
        '''
        
        # Add expandable row for unavailable hotels if any
        if unavailable_hotels:
            row_html += f'''
        <tr class="details-row">
            <td colspan="6">
                <div class="unavailable-details">
                    <strong>Unavailable Properties:</strong>
                    {unavailable_html}
                </div>
            </td>
        </tr>
            '''
        
        destination_rows.append(row_html)
    
    destinations_html = '\n'.join(destination_rows)
    
    # Generate complete HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotel Links Health Dashboard | Sakre Cubes</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1f2937;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            color: #111827;
        }}
        
        .subtitle {{
            color: #6b7280;
            font-size: 1.1rem;
        }}
        
        .status-banner {{
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 16px;
            font-size: 1.1rem;
            background-color: {overall_color};
            color: white;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #111827;
        }}
        
        .stat-label {{
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card.success .stat-value {{
            color: #10b981;
        }}
        
        .stat-card.warning .stat-value {{
            color: #f59e0b;
        }}
        
        .stat-card.error .stat-value {{
            color: #ef4444;
        }}
        
        .main-content {{
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h2 {{
            font-size: 1.75rem;
            margin-bottom: 24px;
            color: #111827;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        thead {{
            background: #f9fafb;
        }}
        
        th {{
            padding: 16px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 16px;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        tr:hover:not(.details-row) {{
            background-color: #f9fafb;
        }}
        
        .details-row {{
            background-color: #fef3c7;
        }}
        
        .details-row td {{
            padding: 16px 32px;
        }}
        
        .unavailable-details {{
            font-size: 0.9rem;
            color: #92400e;
        }}
        
        .unavailable-list {{
            margin-top: 8px;
            margin-left: 20px;
            list-style-type: disc;
        }}
        
        .unavailable-list li {{
            margin: 4px 0;
        }}
        
        .destination-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }}
        
        .destination-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .badge-success {{
            background-color: #d1fae5;
            color: #065f46;
        }}
        
        .badge-warning {{
            background-color: #fed7aa;
            color: #92400e;
        }}
        
        .text-center {{
            text-align: center;
        }}
        
        .text-success {{
            color: #10b981;
            font-weight: 600;
        }}
        
        .text-muted {{
            color: #9ca3af;
        }}
        
        footer {{
            margin-top: 32px;
            text-align: center;
            color: white;
            font-size: 0.9rem;
        }}
        
        footer a {{
            color: white;
            text-decoration: underline;
        }}
        
        .last-update {{
            color: #6b7280;
            font-size: 0.95rem;
            margin-top: 12px;
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.75rem;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 0.85rem;
            }}
            
            th, td {{
                padding: 12px 8px;
            }}
            
            .main-content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏨 Hotel Links Health Dashboard</h1>
            <p class="subtitle">Monitoring Agoda affiliate links across all travel blog posts</p>
            <div class="status-banner">{overall_badge}</div>
            <p class="last-update">Last updated: {last_update}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_destinations}</div>
                <div class="stat-label">Destinations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_hotels}</div>
                <div class="stat-label">Total Hotels</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value">{total_available}</div>
                <div class="stat-label">Available</div>
            </div>
            <div class="stat-card {'error' if (total_unavailable + total_errors) > 0 else 'success'}">
                <div class="stat-value">{total_unavailable + total_errors}</div>
                <div class="stat-label">Issues</div>
            </div>
        </div>
        
        <div class="main-content">
            <h2>Destination Status</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Destination</th>
                        <th class="text-center">Total Hotels</th>
                        <th class="text-center">Available</th>
                        <th class="text-center">Issues</th>
                        <th class="text-center">Status</th>
                        <th class="text-center">Last Checked</th>
                    </tr>
                </thead>
                <tbody>
                    {destinations_html if destinations_html else '<tr><td colspan="6" class="text-center text-muted">No data available</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Automated monitoring via GitHub Actions | <a href="https://github.com/sagarsakre/blog_hotel_links_verifier" target="_blank">View Repository</a></p>
            <p style="margin-top: 8px;">Blog: <a href="https://sakrecubes.com" target="_blank">SakreCubes.com</a></p>
        </footer>
    </div>
</body>
</html>'''
    
    return html


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Generate HTML dashboard from verification results'
    )
    
    parser.add_argument('--input-dir', type=str, default='.',
                       help='Directory containing *_summary.json files (default: current directory)')
    parser.add_argument('--output', type=str, default='index.html',
                       help='Output HTML file path (default: index.html)')
    
    args = parser.parse_args()
    
    print(f"Loading verification results from: {args.input_dir}")
    results = load_verification_results(args.input_dir)
    
    if not results:
        print("Warning: No verification results found!", file=sys.stderr)
        print("Creating dashboard with no data...")
    else:
        print(f"Found {len(results)} destination(s)")
    
    print("Generating HTML dashboard...")
    html = generate_dashboard_html(results)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Dashboard generated: {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
