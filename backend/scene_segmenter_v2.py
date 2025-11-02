"""
Improved scene segmentation module based on scaffold approach.
Uses simpler, more reliable regex patterns.
"""
import re
from typing import List, Dict, Optional, Any


class SceneSegmenter:
    """Segment script text into individual scenes using improved regex."""
    
    # Single comprehensive pattern for scene headers
    SCENE_HDR_RE = re.compile(
        r"^\s*(СЦЕНА|Сцена|SCENE|INT\.|EXT\.|INT/EXT|INT\/EXT|\d{1,4}[\.\-А-ЯЁ]?)",
        re.IGNORECASE | re.MULTILINE
    )
    
    def extract_scene_number(self, header_line: str) -> Optional[str]:
        """Extract scene number from header line."""
        # Try complex formats first
        patterns = [
            r'(\d+[-А-ЯЁ]?\d*[А-ЯЁ]?\d*(?:[-А-ЯЁ]?\d+)*(?:[-\.]\d+)?)',  # 1-11N2, 11-N2, 15-N6-04
            r'(\d+)[Nn](\d+)',  # 11N2 -> returns as 11-N2
            r'(\d+)[/](\w+)',  # 3/П
            r'(\d+[А-Я]?|\d+[-А-ЯЁ]+)',  # 1, 22-Б
            r'(\d+)',  # Simple number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, header_line)
            if match:
                if len(match.groups()) > 1:
                    if 'N' in pattern or 'n' in pattern:
                        return f"{match.group(1)}-N{match.group(2)}"
                    else:
                        return f"{match.group(1)}/{match.group(2)}"
                return match.group(1)
        
        return None
    
    def segment(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into scenes using regex of common script headings.
        
        Returns:
            List of dicts: {scene_number, text, header}
        """
        # Find all scene heading positions
        headings = [(m.start(), m.group(0)) for m in self.SCENE_HDR_RE.finditer(text)]
        
        scenes = []
        
        if not headings:
            # Fallback: split into paragraphs/blocks by double newlines
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            for i, p in enumerate(parts):
                scene_num = self.extract_scene_number(p.split('\n')[0]) or str(i + 1)
                scenes.append({
                    'scene_number': scene_num,
                    'header': p.split('\n')[0] if p.split('\n') else '',
                    'text': p
                })
            return scenes
        
        # Process each scene
        for i, (pos, hdr) in enumerate(headings):
            start = pos
            end = headings[i + 1][0] if i + 1 < len(headings) else len(text)
            
            seg_text = text[start:end].strip()
            
            # Get first line as header
            first_line = seg_text.splitlines()[0] if seg_text.splitlines() else hdr
            
            # Extract scene number
            scene_num = self.extract_scene_number(first_line) or str(i + 1)
            
            # Remove header from text if it's just the scene marker
            if seg_text.startswith(hdr):
                scene_text = seg_text[len(hdr):].strip()
            else:
                scene_text = seg_text
            
            scenes.append({
                'scene_number': scene_num,
                'header': first_line.strip(),
                'text': scene_text
            })
        
        return scenes

