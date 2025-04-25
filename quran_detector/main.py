# main.py
from matcher import qMatcherAnnotater


def main():
    matcher = qMatcherAnnotater()
    sample_text = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"

    annotated = matcher.annotateTxt(sample_text)
    matches = matcher.matchAll(sample_text)

    print("Annotated Text:")
    print(annotated)

    print("\nMatch Records:")
    for match in matches:
        print(match)


if __name__ == "__main__":
    main()
