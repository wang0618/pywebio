// Generate Doc online Demo link

let DEMO_URL;
if (localStorage.getItem('pywebio_doc_demo_url'))
    DEMO_URL = localStorage.getItem('pywebio_doc_demo_url');
else
    DEMO_URL = 'http://pywebio-demos.pywebio.online/doc_demo';

var parseHTML = function (str) {
    let tmp = document.implementation.createHTMLDocument();
    tmp.body.innerHTML = str;
    return tmp.body.children;
};

function ready(fn) {
    if (document.readyState != 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}

let demo_url = new URL(DEMO_URL);

ready(function () {
    let codes = document.querySelectorAll('.demo-cb');
    for (let c of codes) {
        let id = c.getAttribute('id');
        let ele = c.querySelector('.highlight');
        demo_url.searchParams.set("app", id);
        let node = parseHTML(`<a class="viewcode-back" href="${demo_url.href}" target="_blank">[Demo]</a>`)[0];
        ele.insertBefore(node, ele.firstChild);
    }
});

// Translated Version Prompt
const user_lang = (navigator.language || navigator.userLanguage || 'en').toLowerCase().split('-')[0];
const doc_lang = window.location.pathname.split('/')[1].split('-')[0];
if (user_lang !== doc_lang && ['zh', 'en'].indexOf(user_lang) !== -1) {
    let u = new URL(window.location.href);
    let t = u.pathname.split('/');
    t[1] = user_lang === 'en' ? 'en' : 'zh-cn';
    u.pathname = t.join('/');

    let turl = u.href;
    let target_name, summary;
    if (user_lang === 'en') {
        target_name = 'English version';
        summary = 'The English version of this document is available. Switch to ';
    } else {
        target_name = '中文版';
        summary = '本文档有中文版本可用。切换至';
    }
    jQuery.ajax({
        url: turl,
        success: function () {
            jQuery(function () {
                jQuery('.rst-content>.document').before(`
<div style="position: relative;
    padding: 1rem 1rem;
    margin-bottom: 0.8rem;
    margin-top: 0.8rem;
    border: 1px solid transparent;
    border-radius: .25rem;
    color: #0f5132;
    background-color: #d1e7dd;
    border-color: #badbcc;" role="alert">
    ${summary}<a href="${turl}" style="color: #0c4128;font-weight: 700;">${target_name}</a>
</div>`);

                jQuery('body').append(`
<div style="position: fixed;
    font-size: 14px;
    width: auto;
    right: 1rem;
    bottom: 0rem;
    padding: 0.4rem 1rem;
    margin-bottom: 3rem;
    border: 1px solid transparent;
    border-radius: .25rem;
    color: #0f5132;
    background-color: #d1e7dd;
    border-color: #badbcc;" role="alert">
    <span style="vertical-align:middle">
        <svg style="width: 1rem;height: 1rem;fill: currentColor;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04M18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12m-2.62 7l1.62-4.33L19.12 17h-3.24z"></path></svg>
    </span>
    <a href="${turl}" style="color: #0c4128;font-weight: 700;">${target_name}</a>
</div>`);
            })
        },
        dataType: 'html'
    });

}


