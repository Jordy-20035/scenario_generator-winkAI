"""
Scene segmentation module.
Detects scene numbers and splits script text into individual scenes.
"""
import re
from typing import List, Dict, Optional


class SceneSegmenter:
    """Segment script text into individual scenes."""
    
    def __init__(self):
        # Patterns for scene number detection (Russian scripts)
        # Examples: "СЦЕНА 1", "1.", "Сцена 2-А", "3/П", "СЦЕНА 22-Б"
        self.scene_patterns = [
            r'СЦЕНА\s+(\d+[А-Я]?|\d+-\w+)',  # СЦЕНА 1, СЦЕНА 22-Б
            r'Сцена\s+(\d+[А-Я]?|\d+-\w+)',  # Сцена 2-А
            r'^\s*(\d+[А-Я]?|\d+-\w+)[\.\)]\s*',  # 1., 22-Б.
            r'^(\d+)[/](\w+)\s*',  # 3/П
            r'^\s*(\d+)\s*$',  # Standalone number on line
        ]
        
    def extract_scene_number(self, text: str) -> Optional[str]:
        """
        Extract scene number from text line.
        
        Returns:
            Scene number string or None
        """
        text = text.strip()
        
        for pattern in self.scene_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Handle patterns with groups
                if len(match.groups()) > 1:
                    return f"{match.group(1)}/{match.group(2)}"
                else:
                    return match.group(1) if match.group(1) else match.group(0)
        
        return None
    
    def segment(self, text: str) -> List[Dict[str, str]]:
        """
        Segment script text into individual scenes.
        
        Args:
            text: Full script text
        
        Returns:
            List of dictionaries with 'scene_number' and 'text' keys
        """
        scenes = []
        lines = text.split('\n')
        
        current_scene = None
        current_text = []
        
        for line in lines:
            scene_num = self.extract_scene_number(line)
            
            if scene_num:
                # Save previous scene if exists
                if current_scene is not None:
                    scenes.append({
                        'scene_number': current_scene,
                        'text': '\n'.join(current_text).strip()
                    })
                
                # Start new scene
                current_scene = scene_num
                current_text = [line]
            else:
                # Add line to current scene
                if current_scene is not None:
                    current_text.append(line)
                # If no scene started yet, might be header/preface - skip or accumulate
        
        # Don't forget the last scene
        if current_scene is not None:
            scenes.append({
                'scene_number': current_scene,
                'text': '\n'.join(current_text).strip()
            })
        
        # If no scenes found, treat entire text as one scene
        if not scenes:
            scenes.append({
                'scene_number': '1',
                'text': text.strip()
            })
        
        return scenes

