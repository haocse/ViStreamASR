#!/usr/bin/env python3
"""
Speech-to-Text Script using ViStreamASR
A simplified script for converting speech to text using the ViStreamASR library
"""

import os
import sys
import argparse
import json
from datetime import datetime

# Add src directory to path to use local codebase
sys.path.insert(0, 'src')

class SpeechToText:
    """Main class for speech-to-text functionality."""
    
    def __init__(self, chunk_size=640, debug=False):
        """Initialize the speech-to-text engine."""
        self.chunk_size = chunk_size
        self.debug = debug
        self.asr = None
        
    def initialize(self):
        """Initialize the ASR engine."""
        try:
            from streaming import StreamingASR
            self.asr = StreamingASR(chunk_size_ms=self.chunk_size, debug=self.debug)
            if self.debug:
                print("✅ ASR engine initialized successfully")
            return True
        except ImportError as e:
            print(f"❌ Failed to import StreamingASR: {e}")
            return False
    
    def transcribe_file(self, audio_file, output_file=None):
        """Transcribe audio from file."""
        if not os.path.exists(audio_file):
            print(f"❌ Audio file not found: {audio_file}")
            return None
        
        if not self.asr and not self.initialize():
            return None
        
        print(f"🎵 Transcribing file: {audio_file}")
        print("=" * 50)
        
        results = {
            'transcription': '',
            'segments': [],
            'metadata': {
                'file': audio_file,
                'timestamp': datetime.now().isoformat(),
                'chunk_size': self.chunk_size
            }
        }
        
        final_segments = []
        
        try:
            for result in self.asr.stream_from_file(audio_file):
                if result.get('final'):
                    final_text = result['text']
                    final_segments.append(final_text)
                    chunk_info = result.get('chunk_info', {})
                    print(f"✅ Segment {chunk_info.get('chunk_id', '?'):3d}: {final_text}")
            
            # Combine all segments
            complete_text = " ".join(final_segments)
            results['transcription'] = complete_text
            results['segments'] = final_segments
            
            print(f"\n📝 Complete Transcription:")
            print("-" * 40)
            print(complete_text)
            
            # Save results if output file specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 Results saved to: {output_file}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None
    
    def transcribe_microphone(self, duration=10, output_file=None):
        """Transcribe audio from microphone."""
        if not self.asr and not self.initialize():
            return None
        
        try:
            import sounddevice as sd
        except ImportError:
            print("❌ sounddevice library not installed. Install with: pip install sounddevice")
            return None
        
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            if not input_devices:
                print("❌ No input devices (microphones) found")
                return None
        except Exception as e:
            print(f"❌ Error checking audio devices: {e}")
            return None
        
        print(f"🎤 Recording for {duration} seconds...")
        print("🔊 Please speak into your microphone...")
        print("=" * 50)
        
        results = {
            'transcription': '',
            'segments': [],
            'metadata': {
                'source': 'microphone',
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'chunk_size': self.chunk_size
            }
        }
        
        final_segments = []
        
        try:
            for result in self.asr.stream_from_microphone(duration_seconds=duration):
                if result.get('final'):
                    final_text = result['text']
                    final_segments.append(final_text)
                    chunk_info = result.get('chunk_info', {})
                    print(f"✅ Segment {chunk_info.get('chunk_id', '?'):3d}: {final_text}")
            
            # Combine all segments
            complete_text = " ".join(final_segments)
            results['transcription'] = complete_text
            results['segments'] = final_segments
            
            print(f"\n📝 Transcription from microphone:")
            print("-" * 40)
            print(complete_text)
            
            # Save results if output file specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 Results saved to: {output_file}")
            
            return results
            
        except KeyboardInterrupt:
            print("\n⏹️  Recording interrupted by user")
            return None
        except Exception as e:
            print(f"❌ Error during microphone recording: {e}")
            return None
    
    def transcribe_live(self):
        """Continuous live transcription until interrupted."""
        if not self.asr and not self.initialize():
            return None
        
        try:
            import sounddevice as sd
        except ImportError:
            print("❌ sounddevice library not installed. Install with: pip install sounddevice")
            return None
        
        print("🎤 Starting live transcription...")
        print("🔊 Speak freely. Press Ctrl+C to stop.")
        print("=" * 50)
        
        final_segments = []
        
        try:
            for result in self.asr.stream_from_microphone(duration_seconds=None):
                if result.get('partial'):
                    text = result['text'][:60] + "..." if len(result['text']) > 60 else result['text']
                    print(f"🎙️  [PARTIAL] {text}", end='\r')
                
                if result.get('final'):
                    final_text = result['text']
                    final_segments.append(final_text)
                    print(f"\n✅ [FINAL] {final_text}")
            
        except KeyboardInterrupt:
            print("\n⏹️  Live transcription stopped")
            
            if final_segments:
                complete_text = " ".join(final_segments)
                print(f"\n📝 Complete Transcription:")
                print("-" * 40)
                print(complete_text)
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"transcription_{timestamp}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(complete_text)
                print(f"💾 Transcription saved to: {output_file}")
                
                return complete_text
            
            return None

def main():
    parser = argparse.ArgumentParser(
        description="Speech-to-Text using ViStreamASR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python speech_to_text.py --file audio.wav                    # Transcribe file
  python speech_to_text.py --mic --duration 15                   # Record 15s from mic
  python speech_to_text.py --live                                # Continuous live transcription
  python speech_to_text.py --file audio.wav --output results.json # Save results
  python speech_to_text.py --file audio.wav --chunk-size 320     # Smaller chunks
        """
    )
    
    parser.add_argument('--file', type=str, help='Audio file to transcribe')
    parser.add_argument('--mic', action='store_true', help='Use microphone input')
    parser.add_argument('--live', action='store_true', help='Continuous live transcription')
    parser.add_argument('--duration', type=int, default=10, help='Recording duration in seconds (default: 10)')
    parser.add_argument('--chunk-size', type=int, default=640, help='Chunk size in milliseconds (default: 640)')
    parser.add_argument('--output', type=str, help='Output file for results (JSON format)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Create speech-to-text instance
    stt = SpeechToText(chunk_size=args.chunk_size, debug=args.debug)
    
    # Determine mode
    if args.file:
        # File transcription mode
        stt.transcribe_file(args.file, args.output)
        
    elif args.mic:
        # Microphone recording mode
        stt.transcribe_microphone(args.duration, args.output)
        
    elif args.live:
        # Live continuous transcription
        stt.transcribe_live()
        
    else:
        # Interactive mode
        print("🎤 ViStreamASR Speech-to-Text")
        print("=" * 50)
        print("Choose a mode:")
        print("1. Transcribe audio file")
        print("2. Record from microphone")
        print("3. Live continuous transcription")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            file_path = input("Enter audio file path: ").strip()
            if os.path.exists(file_path):
                stt.transcribe_file(file_path)
            else:
                print("❌ File not found")
                
        elif choice == "2":
            duration = int(input("Enter recording duration (seconds): ").strip() or "10")
            stt.transcribe_microphone(duration)
            
        elif choice == "3":
            stt.transcribe_live()
            
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
