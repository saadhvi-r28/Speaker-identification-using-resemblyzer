"""Command-line entrypoint for the Resemblyzer starter utilities."""
import argparse
from pathlib import Path
import sys

from resemblyzer_starter.src.encoder import VoiceEncoderWrapper
from resemblyzer_starter.src.gallery import build_gallery_from_dir, save_gallery_npz
from resemblyzer_starter.src.verify import verify_speaker, identify_speaker


def cmd_build_gallery(args):
    encoder = VoiceEncoderWrapper()
    gallery = build_gallery_from_dir(Path(args.input), encoder)
    save_gallery_npz(gallery, Path(args.output))
    print(f"Saved gallery with {len(gallery)} speakers to {args.output}")


def cmd_verify(args):
    encoder = VoiceEncoderWrapper()
    ok, score = verify_speaker(Path(args.test), args.speaker, Path(args.gallery), encoder, threshold=args.threshold)
    print(f"Similarity={score:.4f} -> {'ACCEPT' if ok else 'REJECT'}")


def cmd_identify(args):
    encoder = VoiceEncoderWrapper()
    best, results = identify_speaker(Path(args.test), Path(args.gallery), encoder, top_k=args.top_k, threshold=args.threshold)
    print("Top matches:")
    for sid, score in results:
        print(f"  {sid}: {score:.4f}")
    if best:
        print(f"Identified as: {best}")
    else:
        print("No match above threshold")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Resemblyzer starter CLI")
    sub = parser.add_subparsers(dest='cmd')

    b = sub.add_parser('build-gallery')
    b.add_argument('--input', required=True, help='Input directory with speaker subfolders')
    b.add_argument('--output', required=True, help='Output NPZ file')
    b.set_defaults(func=cmd_build_gallery)

    v = sub.add_parser('verify')
    v.add_argument('--gallery', required=True)
    v.add_argument('--speaker', required=True)
    v.add_argument('--test', required=True)
    v.add_argument('--threshold', type=float, default=0.75)
    v.set_defaults(func=cmd_verify)

    i = sub.add_parser('identify')
    i.add_argument('--gallery', required=True)
    i.add_argument('--test', required=True)
    i.add_argument('--threshold', type=float, default=0.7)
    i.add_argument('--top-k', dest='top_k', type=int, default=5)
    i.set_defaults(func=cmd_identify)

    args = parser.parse_args(argv)
    if not hasattr(args, 'func') or args.func is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == '__main__':
    main()
