"""
Minimal rule scanner for VoiceDM - QR code to rule loading
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class RuleScanner:
    """Simple rule loader via QR codes"""
    
    def __init__(self, rulesets_dir: str = "server/rulesets"):
        self.rulesets_dir = Path(rulesets_dir)
        self.rulesets_dir.mkdir(exist_ok=True)
        self.loaded_rulesets: Dict[str, Dict] = {}
    
    def load_ruleset(self, qr_data: str) -> Optional[Dict[str, Any]]:
        """
        Load ruleset from QR code data.
        
        QR formats:
        - voicedm://rules/dnd5e/basic
        - {ruleset: "dnd5e", version: "basic"}
        - Direct JSON (for debugging)
        """
        # Try parsing as JSON first
        try:
            data = json.loads(qr_data)
            if isinstance(data, dict) and "ruleset" in data:
                return self._load_named_ruleset(data["ruleset"], data.get("version", "basic"))
        except:
            pass
        
        # Try voicedm:// URL format
        if qr_data.startswith("voicedm://rules/"):
            parts = qr_data.replace("voicedm://rules/", "").split("/")
            if len(parts) >= 1:
                ruleset = parts[0]
                version = parts[1] if len(parts) > 1 else "basic"
                return self._load_named_ruleset(ruleset, version)
        
        # Try direct filename
        if qr_data.endswith(".json"):
            return self._load_file(qr_data)
        
        # Try as simple name (e.g., "dnd5e_basic")
        if "_" in qr_data or qr_data.isalnum():
            return self._load_file(str(self.rulesets_dir / f"{qr_data}.json"))
        
        return None
    
    def _load_named_ruleset(self, ruleset: str, version: str) -> Optional[Dict[str, Any]]:
        """Load a named ruleset from JSON file"""
        cache_key = f"{ruleset}_{version}"
        
        # Check cache
        if cache_key in self.loaded_rulesets:
            return self.loaded_rulesets[cache_key]
        
        # Try to load file
        filename = f"{ruleset}_{version}.json"
        filepath = self.rulesets_dir / filename
        
        if filepath.exists():
            rules = self._load_file(str(filepath))
            if rules:
                self.loaded_rulesets[cache_key] = rules
                return rules
        
        # Fallback to basic if exists
        if version != "basic":
            return self._load_named_ruleset(ruleset, "basic")
        
        return None
    
    def _load_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load rules from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading ruleset {filepath}: {e}")
            return None
    
    def get_available_rulesets(self) -> Dict[str, list]:
        """List available rulesets"""
        available = {}
        for file in self.rulesets_dir.glob("*.json"):
            name = file.stem
            if "_" in name:
                ruleset, version = name.split("_", 1)
                if ruleset not in available:
                    available[ruleset] = []
                available[ruleset].append(version)
            else:
                available[name] = ["default"]
        return available


# Singleton instance
_scanner = RuleScanner()


def scan_qr_code(qr_data: str) -> Optional[Dict[str, Any]]:
    """Quick function to scan QR code and get rules"""
    return _scanner.load_ruleset(qr_data)


def get_rulesets() -> Dict[str, list]:
    """Get list of available rulesets"""
    return _scanner.get_available_rulesets()
