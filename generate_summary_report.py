import os
import glob
import xml.etree.ElementTree as ET
from datetime import datetime

def generate_report(report_dir="test_reports"):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NamoNexus 360° Test Report</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f9f9f9; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .pass { color: #27ae60; font-weight: bold; }
            .fail { color: #c0392b; font-weight: bold; }
            .suite { background: white; margin-bottom: 15px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #ccc; }
            .suite.pass-border { border-left-color: #27ae60; }
            .suite.fail-border { border-left-color: #c0392b; }
            .metrics { display: flex; gap: 20px; margin-bottom: 20px; }
            .metric-box { background: white; padding: 15px; border-radius: 8px; text-align: center; min-width: 100px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            .metric-val { font-size: 24px; font-weight: bold; display: block; }
            .metric-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
            img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; }
            .timestamp { color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🧪 NamoNexus Enterprise v3.5.1 - Test Report</h1>
        <div class="timestamp">Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</div>
    """

    # Process JUnit XMLs
    xml_files = glob.glob(os.path.join(report_dir, "*.xml"))
    total_tests = 0
    total_failures = 0
    
    html += "<h2>Test Suites Execution</h2>"
    
    for xml_file in sorted(xml_files):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
                
            for suite in suites:
                name = os.path.basename(xml_file).replace(".xml", "").replace("_", " ").title()
                tests = int(suite.attrib.get("tests", 0))
                failures = int(suite.attrib.get("failures", 0))
                errors = int(suite.attrib.get("errors", 0))
                total_tests += tests
                total_failures += failures + errors
                
                status = "PASS" if (failures + errors) == 0 else "FAIL"
                border_class = "pass-border" if status == "PASS" else "fail-border"
                status_class = "pass" if status == "PASS" else "fail"
                
                html += f"""
                <div class="suite {border_class}">
                    <h3>{name} <span class="{status_class}" style="float:right">{status}</span></h3>
                    <p>Tests: {tests} | Failures: {failures} | Errors: {errors}</p>
                </div>
                """
        except Exception as e:
            html += f"<p class='fail'>Error parsing {xml_file}: {e}</p>"

    # Load Test Results (Images)
    html += "<h2>Load Test Visualization</h2>"
    if os.path.exists("load_test_rps.png"):
        html += '<div><h3>Throughput (RPS)</h3><img src="../load_test_rps.png"></div>'
    if os.path.exists("load_test_latency.png"):
        html += '<div><h3>Latency (Response Time)</h3><img src="../load_test_latency.png"></div>'
    
    html += "</body></html>"
    
    with open(os.path.join(report_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📊 HTML Report generated: {os.path.join(report_dir, 'index.html')}")

if __name__ == "__main__":
    generate_report()