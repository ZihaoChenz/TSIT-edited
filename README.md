# TSIT-MMIS-Modification

Modified implementation of Multi-Modal Image Synthesis (MMIS) component from TSIT (Time and Style Consistent Image Translation) with enhanced functionality for batch processing and fixed reference image support.

**The original project:** https://github.com/EndlessSora/TSIT

## Key Modifications

1. ​**Fixed Reference Image Support**:
   - Modified architecture to enable all content files to reference a single reference image
   - Eliminates the need for separate references for each content file

2. ​**Batch Processing Capability**:
   - Added `experiment_script.py` for automated batch experiments
   - Supports processing multiple content folders with different weather references

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ZihaoChenz/TSIT-edited.git
   cd TSIT-edited

2. Install requirements
   ```bash
   pip install -r requirements.txt

## Usage

1. Single Image Processing
   ```bash
   python test.py --s_image [reference_image_path] --c_path [content_file_path] ......
   ```
   The contents in ...... are other parameters (refer to the original project)

2. Batch Processing
   ```bash
   python experiment_script.py \
    --test_dir [directory_containing_content_folders] \
    --reference_dir [directory_containing_weather_references]
    --results_root [result path]
   ```

3. Directory Structure Requirements
  ```
  reference_dir/
  ├── cloudy/
  │   ├── ref1.jpg
  │   └── ref2.jpg
  ├── night/
  │   └── ref1.jpg
  ├── rainy/
  │   ├── ref1.jpg
  │   └── ref2.jpg
  └── snowy/
      └── ref1.jpg
  ```






   
   
