# CV-TTS
Common Voice Dataset Filter

## Description
This project filters the Common Voice dataset similarly to the paper "Can we use Common Voice to train a Multi-Speaker TTS system?". It includes functionality for filtering clips, speakers, converting the commonvoice mp3 files to wav files, and computing MOS scores for the clips.


## Installation
1. Clone the repository
2. Install the dependencies using pip:
```bash
pip install -r requirements.txt
```

## Usage
Run the main script with the directory containing the Common Voice dataset files and the output directory for the filtered dataset as arguments. You can also specify the minimum MOS for a speaker to be included in the dataset with the --mos_threshold option. For example:
```bash
python src/main.py /path/to/cv_dir /path/to/output_dir --mos_threshold 3.0
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change, I am willing to help with any issues you may have.

## License
[MIT](LICENSE.md)

## Acknowledgments
- Sewade Ogun, Vincent Colotte, Emmanuel Vincent for the paper "Can we use Common Voice to train a Multi-Speaker TTS system?"
- AndreevP/wvmos for the MOS calculation
- pydub for audio processing
