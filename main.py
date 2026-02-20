"""CLI entry point for bewerbungs-agent."""
import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from bewerbungs_agent import agent


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="bewerbungs-agent – KI-gestützter Bewerbungsmail-Manager",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--inbox",
        default="INBOX",
        help="Gmail-Label, das als Posteingang verwendet wird",
    )
    parser.add_argument(
        "--zusage-label",
        default="Zusagen",
        help="Gmail-Label für Zusagen/Einladungen",
    )
    parser.add_argument(
        "--absage-label",
        default="Absagen",
        help="Gmail-Label für Absagen/Ablehnungen",
    )
    parser.add_argument(
        "--max-emails",
        type=int,
        default=50,
        help="Maximale Anzahl ungelesener E-Mails, die pro Lauf verarbeitet werden",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausführliche Debug-Ausgabe",
    )
    args = parser.parse_args()

    _setup_logging(args.verbose)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Fehler: Die Umgebungsvariable OPENAI_API_KEY ist nicht gesetzt.", file=sys.stderr)
        print("Tipp:   Lege eine .env-Datei an (siehe README) oder setze die Variable direkt.", file=sys.stderr)
        sys.exit(1)

    results = agent.run(
        inbox_label=args.inbox,
        zusage_label=args.zusage_label,
        absage_label=args.absage_label,
        max_emails=args.max_emails,
    )

    print(f"\n{'─'*60}")
    print(f"{'Betreff':<40} {'Kategorie':<12} Aktion")
    print(f"{'─'*60}")
    for r in results:
        subj = r.subject[:38] + ".." if len(r.subject) > 40 else r.subject
        print(f"{subj:<40} {r.category:<12} {r.action_taken}")
    print(f"{'─'*60}")
    print(f"Gesamt: {len(results)} E-Mail(s) verarbeitet.\n")


if __name__ == "__main__":
    main()
