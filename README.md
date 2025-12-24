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

<h1 dir="rtl">quran-detector</h1>

<p dir="rtl">مكتبة لاكتشاف آيات القرآن الكريم ومقاطع الآيات داخل النصوص العربية (تغريدات، مقالات، كتب) مع واجهة Python بسيطة وواجهة سطر أوامر (CLI).</p>

<h2 dir="rtl">المصدر العلمي</h2>

<p dir="rtl">تعتمد الخوارزمية على الورقة البحثية:</p>

<blockquote dir="ltr">
  <p>
    “QDetect: An Intelligent Tool for Detecting Quranic Verses in any Text”<br />
    Samhaa R. El-Beltagy and Ahmed Rafea, Procedia Computer Science 189 (2021) 374–381.<br />
    Paper link: https://www.sciencedirect.com/science/article/pii/S1877050921012321
  </p>
</blockquote>

<p dir="rtl">وهذه الحزمة هي إعادة كتابة حديثة للمستودع القديم:</p>

<p dir="ltr"><a href="https://github.com/SElBeltagy/Quran_Detector" target="_blank">https://github.com/SElBeltagy/Quran_Detector</a></p>

<h2 dir="rtl">مميزات quran-detector</h2>

<ul dir="rtl">
  <li>اكتشاف الآيات والمقاطع داخل نص عربي طويل بكفاءة.</li>
  <li>دعم تصحيح أخطاء إملائية بسيطة (Levenshtein=1) واكتشاف كلمات ناقصة (اختياري).</li>
  <li>واجهة Python صغيرة: <code>detect</code> و <code>annotate</code> و <code>Settings</code>.</li>
  <li>CLI جاهز للاستخدام: <code dir="ltr">quran-detector</code>.</li>
  <li>موارد القرآن مرفقة داخل الحزمة وتُحمّل عبر <code>importlib.resources</code>.</li>
  <li>اختبارات انحدار تعتمد على ملفات golden لضمان ثبات السلوك.</li>
</ul>

<h2 dir="rtl">متطلبات الاستخدام</h2>

<ul dir="rtl">
  <li>Python بإصدار <strong>3.12</strong> أو أحدث.</li>
</ul>

<h2 dir="rtl">تثبيت quran-detector</h2>

<h3 dir="rtl">من خلال <code>uv</code> (موصى به)</h3>

<p dir="rtl">داخل مشروعك:</p>

<pre dir="ltr"><code>uv add quran-detector</code></pre>

<p dir="rtl">إضافات التطوير (للمساهمين):</p>

<pre dir="ltr"><code>uv add --dev "quran-detector[dev]"</code></pre>

<h3 dir="rtl">من خلال <code>pip</code></h3>

<pre dir="ltr"><code>python -m pip install quran-detector</code></pre>

<p dir="rtl">إضافات التطوير:</p>

<pre dir="ltr"><code>python -m pip install "quran-detector[dev]"</code></pre>

<h3 dir="rtl">من خلال الشيفرة المصدرية</h3>

<ul dir="rtl">
  <li>قم بتنزيل المستودع: <code dir="ltr">git clone git@github.com:ieasybooks/quran-detector.git</code></li>
  <li>توجّه إلى مجلد المشروع: <code dir="ltr">cd quran-detector</code></li>
  <li>ثبّت الاعتماديات: <code dir="ltr">uv sync --extra dev</code></li>
</ul>

<p dir="rtl">إذا كنت تستخدم Mise:</p>

<pre dir="ltr"><code>mise exec python@3.12 -- uv sync --extra dev</code></pre>

<h2 dir="rtl">استخدام quran-detector</h2>

<h3 dir="rtl">الاستخدام من خلال سطر الأوامر (CLI)</h3>

<ul dir="rtl">
  <li>اكتشاف (JSON): <code dir="ltr">quran-detector detect --input input.txt &gt; matches.json</code></li>
  <li>وسم: <code dir="ltr">quran-detector annotate --input input.txt &gt; annotated.txt</code></li>
  <li>قراءة من stdin: <code dir="ltr">cat input.txt | quran-detector detect --stdin</code></li>
</ul>

<p dir="rtl">مثال لتغيير الإعدادات:</p>

<pre dir="ltr"><code>quran-detector detect --stdin --no-find-errors --no-find-missing --allowed-error-pct 0.5 --min-match 5</code></pre>

<h3 dir="rtl">الاستخدام من خلال الشيفرة (Python API)</h3>

<p dir="rtl">الواجهة العامة صغيرة ومقصودة:</p>

<ul dir="rtl">
  <li><code>quran_detector.detect(text: str, settings: Settings = Settings()) -&gt; list[dict]</code></li>
  <li><code>quran_detector.annotate(text: str, settings: Settings = Settings()) -&gt; str</code></li>
  <li><code>quran_detector.Settings</code></li>
</ul>

<h4 dir="rtl">مثال: الوسم (Annotate)</h4>

<pre dir="ltr"><code>from quran_detector import Settings, annotate

text = "قال تعالى: وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"
print(annotate(text, settings=Settings(find_missing=False)))</code></pre>

<p dir="rtl">
ملاحظة: خيار <code>find_missing</code> قد يكون عدوانيًا في بعض النصوص العامة (قد يضم كلمات قبل الآية ضمن التطابق). لواجهات المستخدم يُنصح غالبًا بإيقافه:
<code dir="ltr">Settings(find_missing=False)</code>.
</p>

<h4 dir="rtl">مثال: الاكتشاف (Detect)</h4>

<pre dir="ltr"><code>from quran_detector import Settings, detect

text = "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"
matches = detect(text, settings=Settings(find_missing=False))
print(matches)</code></pre>

<h2 dir="rtl">الإعدادات (Settings)</h2>

<p dir="rtl">كائن <code>Settings</code> يتحكم في سلوك المطابقة (وخيارات CLI تُطابقه):</p>

<ul dir="rtl">
  <li><code>find_errors</code>: تفعيل تصحيح أخطاء الإملاء (Levenshtein=1).</li>
  <li><code>find_missing</code>: تفعيل اكتشاف الكلمات الناقصة (مكلف وقد يكون عدوانيًا).</li>
  <li><code>allowed_error_pct</code>: أقصى نسبة أخطاء مسموحة مقارنة بطول التطابق.</li>
  <li><code>min_match</code>: الحد الأدنى لعدد الكلمات في المقطع.</li>
  <li><code>delimiters</code>: تعبير Regex للفصل/التنظيف قبل المطابقة.</li>
</ul>

<h2 dir="rtl">صيغة الخرج</h2>

<h3 dir="rtl">خرج <code>detect()</code></h3>

<p dir="rtl">الدالة <code>detect()</code> تُرجع <code>list[dict]</code> قابلة للتحويل إلى JSON، حيث يحتوي كل سجل على:</p>

<ul dir="rtl">
  <li><code>surah_name</code>: اسم السورة</li>
  <li><code>aya_start</code> و <code>aya_end</code>: رقم الآية أو نطاق الآيات</li>
  <li><code>verses</code>: المقاطع المطابقة (بعد التطبيع)</li>
  <li><code>errors</code>: تفاصيل التصحيحات (إن وجدت)</li>
  <li><code>start_in_text</code> و <code>end_in_text</code>: فهارس كلمات بالنسبة لـ <code>text.split()</code></li>
</ul>

<p dir="rtl">ملاحظة: الفهارس هنا هي مواقع كلمات (وليست إزاحات حروف).</p>

<h3 dir="rtl">خرج <code>annotate()</code></h3>

<p dir="rtl">الدالة <code>annotate()</code> تُرجع النص بعد استبدال المقاطع المطابقة بالنص الأصلي للقرآن مع إضافة مرجع:</p>

<pre dir="ltr"><code>"&lt;quran text&gt;" (سورة:آية[-آية])</code></pre>

<p dir="rtl">
ملاحظة حول الالتباس: بعض المقاطع الشائعة جدًا قد تتطابق مع أكثر من موضع/آية، وقد توجد أكثر من نتيجة صحيحة في حالات معيّنة. اختبارات golden الخاصة بالوسم تتحقق من الحالات غير الملتبسة (unambiguous) فقط.
</p>

<h2 dir="rtl">لمحة عن الخوارزمية</h2>

<p dir="rtl">على مستوى عالٍ، الخوارزمية تقوم بـ:</p>

<ol dir="rtl">
  <li>
    <strong>تطبيع النص</strong>
    <ul dir="rtl">
      <li>تطبيع بعض أشكال الحروف العربية (مثل: أشكال الألف → <code>ا</code>، و <code>ة</code> → <code>ه</code>، و <code>ى/ی</code> → <code>ي</code>).</li>
      <li>إزالة التشكيل لأغراض المطابقة.</li>
    </ul>
  </li>
  <li>
    <strong>فهرسة القرآن</strong>
    <ul dir="rtl">
      <li>بناء بنية trie (“linked hash tables” في الورقة) على جميع سوابق/لواحق مقاطع الآيات (بحد أدنى 3 كلمات).</li>
      <li>تتبع حالات terminal و abs-terminal لدعم “أطول تطابق”.</li>
    </ul>
  </li>
  <li>
    <strong>مسح النص</strong>
    <ul dir="rtl">
      <li>مسح النص كلمة بكلمة ومحاولة تمديد التطابق قدر الإمكان.</li>
      <li>اختياريًا: تصحيح خطأ إملائي بحرف واحد + اكتشاف كلمة ناقصة.</li>
    </ul>
  </li>
  <li>
    <strong>ترشيح النتائج</strong>
    <ul dir="rtl">
      <li>تطبيق حد أدنى للطول (<code>min_match</code>) وحد نسبة الأخطاء (<code>allowed_error_pct</code>) وقواعد إضافية للمقاطع القصيرة.</li>
    </ul>
  </li>
</ol>

<h2 dir="rtl">البيانات / الموارد</h2>

<p dir="rtl">الحزمة ترفق الموارد المطلوبة داخل <code>src/quran_detector/data/</code>:</p>

<ul dir="rtl">
  <li><code>quran-simple.txt</code> (نص القرآن)</li>
  <li><code>quran-index.xml</code> (بيانات السور)</li>
  <li><code>non-terminals.txt</code> (قائمة الكلمات/الوقف)</li>
</ul>

<p dir="rtl">يتم تحميل الموارد عبر <code>importlib.resources</code> لتعمل داخل wheels وعمليات التثبيت المضغوطة.</p>

<h2 dir="rtl">التطوير</h2>

<h3 dir="rtl">pre-commit</h3>

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

<p dir="rtl">الاختبارات تستخدم fixtures مرفقة داخل <code>tests/fixtures/</code> (بدون الاعتماد على مجلدات خارجية).</p>

<p dir="rtl">تشغيل الاختبارات كأوامر منفصلة:</p>

<pre dir="ltr"><code>pytest -q tests/test_tweets_eval.py
pytest -q tests/test_golden_outputs.py -k 'match_all_against_golden'
pytest -q tests/test_golden_outputs.py -k 'annotate_txt_against_golden'</code></pre>

<p dir="rtl">ملاحظة: مجموعات golden ثقيلة عمدًا وقد تأخذ حوالي 30–40 دقيقة لكل مجموعة على جهاز محمول.</p>

