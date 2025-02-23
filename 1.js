function replaceSingleNewlinesWithDouble() {
    var doc = DocumentApp.getActiveDocument();
    var body = doc.getBody();
    var text = body.getText();
    // Replace single newlines with double newlines
    var updatedText = text.replace(/(\n)/g, '\n\n');
    body.setText(updatedText);
}
