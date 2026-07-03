#!/bin/bash
python manual_scorer_parser.py Strategy1/Phase4_Evaluation/eval-S1-locals.json S1_locals blind_S1_locals.json
python manual_scorer_parser.py Strategy1/Phase4_Evaluation/eval-S1-commercial.json S1_commercial blind_S1_commercial.json
python manual_scorer_parser.py Strategy2/Phase4_Evaluation/eval-S2-locals.json S2_locals blind_S2_locals.json
python manual_scorer_parser.py Strategy2/Phase4_Evaluation/eval-S2-commercial.json S2_commercial blind_S2_commercial.json
python manual_scorer_parser.py Strategy3/Phase4_Evaluation/eval-S3-locals.json S3_locals blind_S3_locals.json
python manual_scorer_parser.py Strategy3/Phase4_Evaluation/eval-S3-commercial.json S3_commercial blind_S3_commercial.json