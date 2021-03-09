//lang-chooser has NeedTranslate which is a table that can support any number of languages,
//this is inserted into the html element w/ id "lang-chooser" (see lang_chooser.js:36)



var NeedTranslate = [
    {
        中文: "我2019年从 Wesleyan University 毕业了（化学专业）。毕业了之后不大满意吧，琢磨过了自己的方向好几次。我从小带来了自卑感真的像一只追我的仓鼠，促进我一路成长吧，就是这个不停地要挣脱出。",
        ENG: "I graduated in 2019 from Wesleyan Univeristy (Chemistry major). I was left a little disoriented. Since I was little, I've struggled with feeling less, as if envy a small hamster following me around; this made me grow up fast but with a constant sense that I owe it to myself to at least try to do what I want, for me. Trying to pierce the veil of 'do what is seen as good' to get to 'do what makes you happy' is hard, but worth it everytime.",
    },
    {
        中文: "2020年：成立了自己的YouTube，用不了太久又不满意 （父母的压力，肩膀受不了），去Genentech公司工作了。",
        ENG: "In 2020, I started my YouTube channel, but shortly after (a month or two), I went to work at Genentech.",
    },
    {
        中文: "2021年：上 Metis 的数据分析，3月内就造成了所有的 Portoflio。",
        ENG: "In 2021, I attended the Metis Data Science program, and made this website portfolio in 3 months.",
    },
    {
        中文: "我学了3年的中文了 （2018年开始的，去过北京3个月）",
        ENG: "I've been studying Mandarin for 3 years, and went to Beijing for 3 months in 2018",
    },
    {
        中文: "身份：",
        ENG: "Identity: ",
    },
    {
        中文: "中文（3.5年），钢琴（8年），诗（？？年），🏃（？？）",
        ENG: "Mandarin (3.5 yrs); piano (8 yrs); poem (?? yrs); 🏃(??)",
    },
    {
        中文: "登录",
        ENG: "Login",
    },
    {
        中文: "用户名",
        ENG: "Username",
    },
    {
        中文: "密码",
        ENG: "Password"
    }
];
var usable_codes = [
  {
    code: "cn",
    name: "中文",
  },
  // More country codes
];
var current_lang;
var translate = function({
    dropID = "lang-chooser", //id of html element to be made into language selector dropdown
    stringAttribute = "data-translate-text",
    chosenLang = "ENG",
    NeedTranslate = NeedTranslate,
    countryCodes = false,
    countryCodeData = [],
} = {}) {
    const root = document.documentElement;

    var supported_languages = Object.keys(NeedTranslate[0]);
    current_lang = chosenLang;

    (function createMLDrop() {
        var language_menu = document.getElementById(dropID);
        // Reset the menu
        language_menu.innerHTML = "";
        // Now build the options
        supported_languages.forEach((lang, langidx) => {
            let HTMLoption = document.createElement("option");
            HTMLoption.value = lang;
            console.log(lang)
            HTMLoption.textContent = lang;
            language_menu.appendChild(HTMLoption);

            if (lang === chosenLang) {
                language_menu.value = lang;
            }
        });
        language_menu.addEventListener("change", function(e) {

            current_lang = language_menu[language_menu.selectedIndex].value;
            translate_everything();
            // Here we update the 2-digit lang attribute if required
            if (countryCodes === true) {
                if (!Array.isArray(countryCodeData) || !countryCodeData.length) {
                    console.warn("Cannot access strings for language codes");
                    return;
                }
                // throws error still ... have to figure out country codes root.setAttribute("lang", updateCountryCodeOnHTML().code);
            }
        });
    })();

    function updateCountryCodeOnHTML() {
        return countryCodeData.find(this2Digit => this2Digit.name === current_lang);
    }

    function translate_everything() {
        let everyword = document.querySelectorAll(`[${stringAttribute}]`);
        everyword.forEach(each_word => {
            let old_word = each_word.textContent;
            let translated_word = translate_one_word(old_word, NeedTranslate);
            each_word.textContent = translated_word;
            each_word.classList.remove('中文', 'ENG')
            each_word.classList.add(current_lang)
        });
    }


};

function translate_one_word(each_word, NeedTranslate) {
    var word_matched_to_NeedTranslate = NeedTranslate.find(function(stringObj) {
        // Create an array of the objects values:
        let stringValues = Object.values(stringObj);
        // Now return if we can find that string anywhere in there
        return stringValues.includes(each_word);
    });
    if (word_matched_to_NeedTranslate) {
        return word_matched_to_NeedTranslate[current_lang];
    } else {
        // If we don't have a match in our language strings, return the original
        return each_word;
    }
}

translate({
    dropID: "lang-chooser",
    stringAttribute: "data-mlr-text", //any span tag w/ data-mlr-text will be translated as is specified in NeedTranslate table
    chosenLang: "中文",
    NeedTranslate: NeedTranslate,
    countryCodes: true,
    countryCodeData: usable_codes,
});
