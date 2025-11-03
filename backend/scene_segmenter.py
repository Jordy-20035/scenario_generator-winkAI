import re
from typing import List, Dict, Optional, Any

class SceneSegmenter:
    """Segment script text into individual scenes using improved regex."""
    
    SCENE_HDR_RE = re.compile(
        r"^\s*(СЦЕНА|Сцена|SCENE|INT\.|EXT\.|INT/EXT|INT\/EXT|\d{1,4}[\.\-А-ЯЁ]?)",
        re.IGNORECASE | re.MULTILINE
    )
    
    def extract_scene_number(self, header_line: str) -> Optional[str]:
        """Extract scene number from header line."""
        patterns = [
            r'(\d+[-А-ЯЁ]?\d*[А-ЯЁ]?\d*(?:[-А-ЯЁ]?\d+)*(?:[-\.]\d+)?)', 
            r'(\d+)[Nn](\d+)',  
            r'(\d+)[/](\w+)',  
            r'(\d+[А-Я]?|\d+[-А-ЯЁ]+)',  
            r'(\d+)'
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
        headings = [(m.start(), m.group(0)) for m in self.SCENE_HDR_RE.finditer(text)]
        scenes = []
        
        if not headings:
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            for i, p in enumerate(parts):
                scene_num = self.extract_scene_number(p.split('\n')[0]) or str(i + 1)
                scenes.append({
                    'scene_number': scene_num,
                    'header': p.split('\n')[0] if p.split('\n') else '',
                    'text': p
                })
            return scenes
        
        for i, (pos, hdr) in enumerate(headings):
            start = pos
            end = headings[i + 1][0] if i + 1 < len(headings) else len(text)
            seg_text = text[start:end].strip()
            first_line = seg_text.splitlines()[0] if seg_text.splitlines() else hdr
            scene_num = self.extract_scene_number(first_line) or str(i + 1)
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

