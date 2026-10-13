(function () {
  // 模块显示开关：true 显示，false 隐藏。默认全部开启。
  // 前面与背面的模板各有一份配置，编辑 Anki 模板时请分别修改。
  var modules = {
    frequency: true,
    wordAudio: true,
    ipa: true,
    meaning: true,
    englishDefinition: true,
    morphology: true,
    wordFamily: true,
    derivatives: true,
    examples: true,
    examExamples: true,
    updateCheck: true,
    sources: true
  };
  var sides = document.querySelectorAll('main.CardSide');
  for (var i = 0; i < sides.length; i++) {
    var elements = sides[i].querySelectorAll('[data-module]');
    for (var j = 0; j < elements.length; j++) {
      elements[j].hidden = modules[elements[j].getAttribute('data-module')] === false;
    }
  }
})();
