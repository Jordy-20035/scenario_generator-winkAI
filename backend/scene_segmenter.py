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
        # Examples: "СЦЕНА 1", "1.", "Сцена 2-А", "3/П", "СЦЕНА 22-Б", "11-N2", "1-11N2", "15-N6-04"
        self.scene_patterns = [
            # Explicit "СЦЕНА" or "Сцена" prefix
            r'СЦЕНА\s+(\d+(?:[-А-ЯЁ]?\d*[А-ЯЁ]?\d*(?:[-\.]?[А-ЯЁ]?\d+)?)?)',  # СЦЕНА 11-N2, СЦЕНА 1-11N2
            r'Сцена\s+(\d+(?:[-А-ЯЁ]?\d*[А-ЯЁ]?\d*(?:[-\.]?[А-ЯЁ]?\d+)?)?)',  # Сцена 11-N2
            # Complex scene formats at start of line: 11-N2, 1-11N2, 15-N6-04
            r'^\s*(\d+[-А-ЯЁ]?\d*[А-ЯЁ]?\d*(?:[-А-ЯЁ]?\d+)*(?:[-\.]\d+)?)\s*[\.\)]\s*',  # 1-11N2., 11-N2., 15-N6-04.
            r'^\s*(\d+[-А-ЯЁ\.]+\w*(?:-\d+)?)\s*[\.\)]?\s*',  # 1-11N2, 11-N2, 15-N6-04
            # Format with N: 11N2, 15N6 -> becomes 11-N2, 15-N6 (if we want to standardize)
            r'^(\d+)[Nn](\d+)\s*',  # 11N2, 15N6 -> will be formatted as 11-N2, 15-N6
            # Format with slash: 3/П
            r'^(\d+)[/](\w+)\s*',  # 3/П
            # Simple formats: 1., 22-Б.
            r'^\s*(\d+[А-Я]?|\d+[-А-ЯЁ]+)[\.\)]\s*',  # 1., 22-Б.
            # Standalone number (last resort)
            r'^\s*(\d+)\s*$',  # Standalone number on line
        ]
        
    def extract_scene_number(self, text: str) -> Optional[str]:
        """
        Extract scene number from text line.
        Preserves full scene identifier format (e.g., "11-N2", "1-11N2", "15-N6-04").
        
        Returns:
            Scene number string or None
        """
        text = text.strip()
        
        for pattern in self.scene_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Handle patterns with groups (like 3/П or 11N2)
                if len(match.groups()) > 1:
                    # Format with slash: 3/П -> 3/П
                    if '/' in pattern or '[/]' in pattern:
                        return f"{match.group(1)}/{match.group(2)}"
                    # Format with N: 11N2 -> 11-N2 (standardize)
                    elif '[Nn]' in pattern:
                        return f"{match.group(1)}-N{match.group(2)}"
                    else:
                        return f"{match.group(1)}-{match.group(2)}"
                else:
                    scene_num = match.group(1) if match.group(1) else match.group(0)
                    # Clean up - remove trailing punctuation that might have been captured
                    scene_num = scene_num.rstrip('.,)')
                    return scene_num
        
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

