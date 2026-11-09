package org.iowo.d4.biblestudy;

import android.content.Context;
import android.graphics.*;
import android.graphics.pdf.PdfDocument;
import android.text.*;
import android.text.style.*;
import org.json.*;
import java.io.ByteArrayOutputStream;

/** Exports validated structured sermon text using Android's Unicode renderer. */
final class SermonPdf {
    private static final int WIDTH = 595, HEIGHT = 842, MARGIN = 36;
    private final PdfDocument document = new PdfDocument();
    private PdfDocument.Page page;
    private int number;
    private float y;
    private final Typeface[] fonts = new Typeface[4];

    private SermonPdf(Context context) {
        String[] names = {"Regular", "Bold", "Italic", "BoldItalic"};
        for (int i = 0; i < names.length; i++) {
            fonts[i] = Typeface.createFromAsset(context.getAssets(), "runtime/static/fonts/NotoSans-"+names[i]+".ttf");
        }
    }

    private void finishPage() {
        if (page == null) return;
        Paint footer = new Paint(Paint.ANTI_ALIAS_FLAG);
        footer.setTextSize(8); footer.setColor(Color.DKGRAY); footer.setTextAlign(Paint.Align.RIGHT);
        page.getCanvas().drawText(Integer.toString(number), WIDTH-MARGIN, HEIGHT-24, footer);
        document.finishPage(page); page = null;
    }

    private void nextPage() {
        finishPage();
        page = document.startPage(new PdfDocument.PageInfo.Builder(WIDTH, HEIGHT, ++number).create());
        page.getCanvas().drawColor(Color.WHITE); y = MARGIN;
    }

    private Typeface typeface(JSONObject run, boolean boldDefault, boolean italicDefault) {
        boolean bold = run.optBoolean("bold", boldDefault), italic = run.optBoolean("italic", italicDefault);
        int style = bold ? (italic ? Typeface.BOLD_ITALIC : Typeface.BOLD) : (italic ? Typeface.ITALIC : Typeface.NORMAL);
        String family = run.optString("font_family", "Noto Sans");
        if (family.equals("Courier New")) return Typeface.create(Typeface.MONOSPACE, style);
        if (family.equals("Times New Roman") || family.equals("Cambria") || family.equals("Georgia"))
            return Typeface.create(Typeface.SERIF, style);
        return fonts[style];
    }

    private static final class FontSpan extends MetricAffectingSpan {
        private final Typeface face;
        FontSpan(Typeface face) { this.face = face; }
        @Override public void updateDrawState(TextPaint paint) { paint.setTypeface(face); }
        @Override public void updateMeasureState(TextPaint paint) { paint.setTypeface(face); }
    }

    private static void span(SpannableStringBuilder text, Object style, int start) {
        if (text.length() > start) text.setSpan(style, start, text.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
    }

    private void block(JSONObject block, boolean imported) throws Exception {
        String kind = block.optString("type", "paragraph");
        boolean bold = kind.equals("main_point") || kind.equals("subpoint") || kind.equals("heading") || kind.equals("conclusion");
        boolean italic = kind.equals("scripture");
        SpannableStringBuilder text = new SpannableStringBuilder();
        JSONArray runs = block.getJSONArray("runs");
        float largest = 11;
        for (int i = 0; i < runs.length(); i++) {
            JSONObject run = runs.getJSONObject(i); int start = text.length();
            text.append(run.getString("text"));
            span(text, new FontSpan(typeface(run,bold,italic)),start);
            float size = (float) Math.max(6,Math.min(72,run.optDouble("font_size",11)));
            largest = Math.max(largest,size);
            span(text,new AbsoluteSizeSpan(Math.round(size)),start);
            if (run.optBoolean("underline")) span(text,new UnderlineSpan(),start);
            if (run.optBoolean("superscript")) span(text,new SuperscriptSpan(),start);
            if (run.has("color")) span(text,new ForegroundColorSpan(Color.parseColor(run.getString("color"))),start);
            if (run.has("highlight")) span(text,new BackgroundColorSpan(Color.parseColor(run.getString("highlight"))),start);
        }
        if (text.length()==0) text.append(" ");
        int defaultIndent = kind.equals("subpoint") || kind.equals("illustration") ? 18 : kind.equals("sub_subpoint") ? 36 : 0;
        int indent = (int)Math.max(0,Math.min(160,block.optDouble("indent",defaultIndent)));
        TextPaint paint = new TextPaint(Paint.ANTI_ALIAS_FLAG | Paint.SUBPIXEL_TEXT_FLAG);
        paint.setTypeface(fonts[0]); paint.setTextSize(11); paint.setColor(Color.BLACK);
        String alignment = block.optString("align","left");
        Layout.Alignment align = alignment.equals("center") ? Layout.Alignment.ALIGN_CENTER :
            alignment.equals("right") ? Layout.Alignment.ALIGN_OPPOSITE : Layout.Alignment.ALIGN_NORMAL;
        StaticLayout.Builder builder = StaticLayout.Builder.obtain(text,0,text.length(),paint,WIDTH-2*MARGIN-indent)
            .setAlignment(align).setIncludePad(false).setLineSpacing(imported?0:2,1.0f)
            .setBreakStrategy(android.graphics.text.LineBreaker.BREAK_STRATEGY_HIGH_QUALITY);
        if (alignment.equals("justify")) builder.setJustificationMode(android.graphics.text.LineBreaker.JUSTIFICATION_MODE_INTER_WORD);
        StaticLayout layout = builder.build();
        if (page == null || (block.optBoolean("page_break") && y>MARGIN)) nextPage();
        boolean heading = kind.equals("main_point") || kind.equals("subpoint") || kind.equals("heading") || kind.equals("theme") || kind.equals("text");
        if (heading && y>MARGIN && HEIGHT-MARGIN-y < Math.min(layout.getHeight(),largest*2)+24) nextPage();
        int start = 0;
        while (start < layout.getLineCount()) {
            int top = layout.getLineTop(start), end = start;
            float available = HEIGHT-MARGIN-y;
            while (end < layout.getLineCount() && layout.getLineBottom(end)-top <= available) end++;
            if (end == start) {
                if (y>MARGIN) { nextPage(); continue; }
                end++; // A validated maximum font size always fits a blank page.
            }
            int bottom = layout.getLineBottom(end-1);
            Canvas canvas = page.getCanvas();
            canvas.save(); canvas.clipRect(MARGIN+indent,y,WIDTH-MARGIN,y+bottom-top);
            canvas.translate(MARGIN+indent,y-top); layout.draw(canvas); canvas.restore();
            y += bottom-top; start = end;
            if (start < layout.getLineCount()) nextPage();
        }
        y += (float)Math.max(0,Math.min(36,block.optDouble("space_after",8)));
    }

    static byte[] create(Context context, String json) throws Exception {
        JSONObject note = new JSONObject(json);
        SermonPdf output = new SermonPdf(context);
        try {
            JSONArray blocks = note.getJSONObject("content").getJSONArray("blocks");
            boolean imported = note.optJSONObject("origin") != null && note.getJSONObject("origin").has("source_id");
            for (int i=0; i<blocks.length(); i++) output.block(blocks.getJSONObject(i),imported);
            if (output.page == null) output.nextPage();
            output.finishPage();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            output.document.writeTo(bytes); return bytes.toByteArray();
        } finally {
            output.finishPage(); output.document.close();
        }
    }
}
