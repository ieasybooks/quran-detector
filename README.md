<div align="center">
  <a href="https://pypi.org/project/quran-detector" target="_blank"><img src="https://img.shields.io/pypi/v/quran-detector?label=PyPI%20Version&color=limegreen" /></a>
  <a href="https://pypi.org/project/quran-detector" target="_blank"><img src="https://img.shields.io/pypi/pyversions/quran-detector?color=limegreen" /></a>
  <a href="https://github.com/ieasybooks/quran-detector/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/pypi/l/quran-detector?color=limegreen" /></a>
  <a href="https://pepy.tech/project/quran-detector" target="_blank"><img src="https://static.pepy.tech/badge/quran-detector" /></a>
  <a href="https://github.com/ieasybooks/quran-detector/actions/workflows/pre-commit.yml" target="_blank"><img src="https://github.com/ieasybooks/quran-detector/actions/workflows/pre-commit.yml/badge.svg" /></a>
</div>

<div align="center">

  [![ar](https://img.shields.io/badge/lang-ar-brightgreen.svg)](README.md)
  [![en](https://img.shields.io/badge/lang-en-red.svg)](README.en.md)

</div>

<h2 dir="rtl">quran-detector</h2>

<p dir="rtl">
مكتبة لاكتشاف آيات القرآن الكريم ومقاطع الآيات داخل النصوص العربية (تغريدات، مقالات، كتب) اعتمادًا على خوارزمية مبنية على الورقة البحثية التالية:
</p>

<blockquote dir="ltr">
  <p>
    “QDetect: An Intelligent Tool for Detecting Quranic Verses in any Text”<br />
    Samhaa R. El-Beltagy and Ahmed Rafea, Procedia Computer Science 189 (2021) 374–381.
    <br />
    Paper link: https://www.sciencedirect.com/science/article/pii/S1877050921012321
    <br />
    Legacy implementation repo: https://github.com/SElBeltagy/Quran_Detector
  </p>
</blockquote>

<p dir="rtl">
هذا المشروع هو إعادة كتابة حديثة للمشروع القديم <code>Quran_Detector</code> مع واجهة Python واضحة، وأداة سطر أوامر (CLI)، وملفات بيانات مرفقة (نص القرآن وقوائم الكلمات)، واختبارات انحدار (golden files) لضمان ثبات السلوك.
</p>

<h2 dir="rtl">التثبيت</h2>

<h3 dir="rtl">باستخدام <code>uv</code> (موصى به)</h3>

<p dir="rtl">داخل مشروعك:</p>

<pre dir="ltr"><code>uv add quran-detector</code></pre>

<p dir="rtl">للتطوير (يضيف <code>ruff</code> و <code>mypy</code> و <code>pre-commit</code>):</p>

<pre dir="ltr"><code>uv add --dev "quran-detector[dev]"</code></pre>

<h3 dir="rtl">باستخدام <code>pip</code></h3>

<pre dir="ltr"><code>python -m pip install quran-detector</code></pre>

<p dir="rtl">إضافات التطوير:</p>

<pre dir="ltr"><code>python -m pip install "quran-detector[dev]"</code></pre>

<h3 dir="rtl">تهيئة المستودع محليًا (هذا المستودع)</h3>

<p dir="rtl">هذا المستودع يحتوي على <code>uv.lock</code> لذلك يمكنك تشغيل:</p>

<pre dir="ltr"><code>uv sync --extra dev</code></pre>

<p dir="rtl">إذا كنت تستخدم Mise:</p>

<pre dir="ltr"><code>mise exec python@3.12 -- uv sync --extra dev</code></pre>

<h2 dir="rtl">بداية سريعة</h2>

<h3 dir="rtl">واجهة Python</h3>

<pre dir="ltr"><code>from quran_detector import Settings, detect, annotate

text = "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"

records = detect(text, settings=Settings())
annotated = annotate(text, settings=Settings())</code></pre>

<h3 dir="rtl">أداة سطر الأوامر (CLI)</h3>

<p dir="rtl">اكتشاف (خرج JSON):</p>

<pre dir="ltr"><code>quran-detector detect --input input.txt &gt; matches.json</code></pre>

<p dir="rtl">وسم/تعليق (يضيف مراجع الآيات داخل النص الناتج):</p>

<pre dir="ltr"><code>quran-detector annotate --input input.txt &gt; annotated.txt</code></pre>

<p dir="rtl">القراءة من stdin:</p>

<pre dir="ltr"><code>cat input.txt | quran-detector detect --stdin</code></pre>

<h2 dir="rtl">الواجهة العامة (Public API)</h2>

<p dir="rtl">الواجهة العامة مقصودة لتكون صغيرة وبسيطة:</p>

<ul dir="rtl">
  <li><code>quran_detector.detect(text: str, settings: Settings = Settings()) -&gt; list[dict]</code></li>
  <li><code>quran_detector.annotate(text: str, settings: Settings = Settings()) -&gt; str</code></li>
  <li><code>quran_detector.Settings</code> (كائن إعدادات)</li>
</ul>

<p dir="rtl">
داخليًا، يتم إنشاء كائن <code>Engine</code> وحيد (singleton) عند أول استدعاء بشكل كسول، ويعتمد على موارد القرآن المرفقة داخل الحزمة.
</p>

<h2 dir="rtl">صيغة الخرج</h2>

<p dir="rtl">
الدالة <code>detect()</code> تُرجع <code>list[dict]</code> قابلة للتحويل إلى JSON، حيث يحتوي كل سجل على:
</p>

<ul dir="rtl">
  <li><code>surah_name</code>: اسم السورة (نص عربي)</li>
  <li><code>aya_start</code> و <code>aya_end</code>: نطاق الآية (شاملًا)</li>
  <li><code>verses</code>: قائمة بمقاطع/نصوص التطابق (بعد التطبيع)</li>
  <li><code>errors</code>: قائمة قوائم تشرح التصحيحات لكل مقطع</li>
  <li><code>start_in_text</code> و <code>end_in_text</code>: فهارس كلمات بالنسبة لـ <code>text.split()</code> بعد تجهيز الرموز داخليًا</li>
</ul>

<p dir="rtl"><strong>ملاحظات:</strong></p>

<ul dir="rtl">
  <li>الفهارس هي <strong>مواقع كلمات</strong> وليست إزاحات حروف.</li>
  <li>إذا كان التطابق يغطي أكثر من آية متتالية فستجد <code>aya_end &gt; aya_start</code> و <code>verses</code> تحتوي أكثر من مقطع.</li>
 </ul>

<h2 dir="rtl">الإعدادات (<code>Settings</code>)</h2>

<p dir="rtl">كائن <code>Settings</code> يتحكم في سلوك المطابقة:</p>

<ul dir="rtl">
  <li><code>find_errors: bool = True</code><br />
  تفعيل تصحيح أخطاء الإملاء (مسافة Levenshtein تساوي 1 بين كلمة الإدخال وأحد أبناء العقدة في الـ trie).</li>
  <li><code>find_missing: bool = True</code><br />
  تفعيل اكتشاف الكلمات الناقصة عبر السماح بـ “تخطّي” كلمة داخل مسار الـ trie (مكلف حسابيًا؛ انظر الورقة).</li>
  <li><code>allowed_error_pct: float = 0.25</code><br />
  أقصى نسبة للأخطاء المسموحة مقارنة بطول التطابق (عدد الكلمات). السجلات التي تتجاوز هذا الحد يتم استبعادها.</li>
  <li><code>min_match: int = 3</code><br />
  الحد الأدنى لعدد الكلمات لتكوين مقطع صالح (الافتراضي في الورقة هو 3).</li>
  <li><code>delimiters: str = GLOBAL_DELIMITERS</code><br />
  تعبير Regex لفصل/إزالة علامات الترقيم من الكلمات قبل المطابقة.</li>
</ul>

<p dir="rtl">خيارات CLI تُطابق هذه الحقول 1:1:</p>

<pre dir="ltr"><code>quran-detector detect --stdin --no-find-errors --no-find-missing --allowed-error-pct 0.5 --min-match 5</code></pre>

<h2 dir="rtl">كيف يعمل الوسم (Annotation)</h2>

<p dir="rtl">
الدالة <code>annotate()</code> تُرجع نصًا يتم فيه استبدال المقاطع المطابقة بالنص الأصلي للقرآن (كما هو مخزّن في الموارد المرفقة)
مع إضافة وسم مرجعي:
</p>

<pre dir="ltr"><code>"&lt;quran text&gt;"(سورة:آية[-آية])</code></pre>

<p dir="rtl">
ملاحظة حول الالتباس: بعض المقاطع الشائعة جدًا قد تتطابق مع أكثر من موضع/آية. الخوارزمية القديمة (وبالتالي هذه الإعادة)
قد تُنتج أكثر من نتيجة صحيحة في حالات معيّنة. لذلك اختبارات golden الخاصة بالوسم تتحقق من الحالات غير الملتبسة (unambiguous) فقط.
</p>

<h2 dir="rtl">لمحة عن الخوارزمية (QDetect)</h2>

<p dir="rtl">
على مستوى عالٍ، هذه طريقة مطابقة أنماط متعددة مستوحاة من Aho–Corasick، لكنها في الورقة مُنفّذة عبر “linked hash tables”،
وفي هذا المشروع تُنفّذ ببنية trie مخصصة لاكتشاف مقاطع الآيات بكفاءة.
</p>

<ol dir="rtl">
  <li><strong>التطبيع (Normalization)</strong>
    <ul>
      <li>تطبيع بعض أشكال الحروف العربية (مثل: أشكال الألف → <code>ا</code>، و <code>ة</code> → <code>ه</code>، و <code>ى/ی</code> → <code>ي</code>).</li>
      <li>إزالة التشكيل/الضبط من نصوص القرآن والمدخل لأغراض المطابقة.</li>
    </ul>
  </li>
  <li><strong>فهرسة القرآن</strong>
    <ul>
      <li>بناء بنية trie (“linked hash tables” في الورقة) على <strong>جميع سوابق/لواحق مقاطع الآيات</strong> (بحد أدنى 3 كلمات).</li>
      <li>تتبع حالات terminal و abs-terminal لدعم “أطول تطابق” (longest match).</li>
    </ul>
  </li>
  <li><strong>المسح (Scanning)</strong>
    <ul>
      <li>مسح النص كلمة بكلمة ومحاولة تمديد التطابق قدر الإمكان.</li>
      <li>اختياريًا:
        <ul>
          <li>تصحيح خطأ إملائي بحرف واحد.</li>
          <li>اكتشاف كلمة مفقودة.</li>
        </ul>
      </li>
    </ul>
  </li>
  <li><strong>الترشيح (Filtering)</strong>
    <ul>
      <li>تطبيق حد أدنى للطول، واستبعاد بعض العبارات/الآيات القصيرة الشائعة، وتطبيق حد نسبة الأخطاء <code>allowed_error_pct</code>.</li>
      <li>تطبيق معيار نسبة كلمات الوقف للمقاطع القصيرة (سلوك الورقة/الإرث).</li>
    </ul>
  </li>
</ol>

<p dir="rtl">
للتفاصيل النظرية والخوارزمية، راجع الورقة البحثية من خلال الرابط في الأعلى.
</p>

<h2 dir="rtl">البيانات / الموارد</h2>

<p dir="rtl">الحزمة ترفق الموارد المطلوبة داخل <code>src/quran_detector/data/</code>:</p>

<ul dir="rtl">
  <li><code>quran-simple.txt</code> (نص القرآن)</li>
  <li><code>quran-index.xml</code> (بيانات السور)</li>
  <li><code>non-terminals.txt</code> (قائمة كلمات الوقف / non-terminals)</li>
</ul>

<p dir="rtl">
يتم تحميل الموارد عبر <code>importlib.resources</code> بحيث تعمل في حزم wheels وعمليات التثبيت المضغوطة.
</p>

<h2 dir="rtl">التطوير</h2>

<h3 dir="rtl">Pre-commit</h3>

<p dir="rtl">هذا المستودع يستخدم:</p>

<ul dir="rtl">
  <li><code>ruff</code> (lint + ترتيب الاستيرادات)</li>
  <li><code>ruff format</code> (تنسيق)</li>
  <li><code>mypy</code> (فحص الأنواع)</li>
</ul>

<p dir="rtl">تثبيت hooks:</p>

<pre dir="ltr"><code>pre-commit install</code></pre>

<p dir="rtl">تشغيلها على كل الملفات:</p>

<pre dir="ltr"><code>pre-commit run --all-files</code></pre>

<h3 dir="rtl">الاختبارات</h3>

<p dir="rtl">
الاختبارات تستخدم fixtures مرفقة داخل <code>tests/fixtures/</code> (بدون الاعتماد على مجلدات خارجية).
</p>

<p dir="rtl">تشغيل الاختبارات كأوامر منفصلة:</p>

<pre dir="ltr"><code>pytest -q tests/test_tweets_eval.py
pytest -q tests/test_golden_outputs.py -k 'match_all_against_golden'
pytest -q tests/test_golden_outputs.py -k 'annotate_txt_against_golden'</code></pre>

<p dir="rtl">
ملاحظة: مجموعات golden ثقيلة عمدًا وقد تأخذ حوالي 30–40 دقيقة لكل مجموعة على جهاز محمول.
</p>
