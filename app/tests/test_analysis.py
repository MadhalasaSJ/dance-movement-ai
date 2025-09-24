import pytest
from app.analysis import get_pose_actions, analyze
import os

# Sample landmarks for testing (33 keypoints, simplified)
sample_landmarks = [{"x":0, "y":0, "z":0, "visibility":1.0} for _ in range(33)]

def test_get_pose_actions_structure():
    actions = get_pose_actions(sample_landmarks)
    # Check all expected keys are present
    assert "left_arm" in actions
    assert "right_arm" in actions
    assert "left_leg" in actions
    assert "right_leg" in actions

def test_analyze_creates_outputs(tmp_path):
    test_video = "tests/sample_video.mp4"  # You can include a tiny dummy mp4
    output_video = tmp_path / "annotated.mp4"
    output_json = tmp_path / "output.json"
    
    # Run analysis
    analyze(test_video, str(output_video), str(output_json))
    
    # Assert files were created
    assert output_video.exists()
    assert output_json.exists()
    
    # Optionally, check JSON structure
    import json
    with open(output_json) as f:
        data = json.load(f)
    assert "summary" in data
    assert "frames" in data
