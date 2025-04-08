# main.py
from matcher import QuranMatcherAnnotator


def main():
    matcher = QuranMatcherAnnotator()
    sample_text = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"

    annotated = matcher.annotate_text(sample_text)
    matches = matcher.match_all(sample_text)

    print("Annotated Text:")
    print(annotated)

    print("\nMatch Records:")
    for match in matches:
        print(match)


if __name__ == "__main__":
    main()
