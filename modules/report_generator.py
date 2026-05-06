import os

def generate_report(input_file):
    output_folder = "outputs"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(output_folder, "generated_report.txt")

    with open(output_file, "w") as f:
        f.write(f"Report generated successfully from {input_file}")

    return output_file