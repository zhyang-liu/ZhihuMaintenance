// ==UserScript==
// @name       ZhihuSearchPageQuickReport
// @namespace  http://lzy.in/
// @version    0.3
// @description  Nothing is useful.
// @match      http://www.zhihu.com/search?*
// @copyright  2014+, 知乎 @刘中阳
// ==/UserScript==

var batch_report_xsrf = $('input[name="_xsrf"]').attr('value');

var reportQuestionBtnOnclick = function() {
    doReport($(this).attr('report-id'),'question', '1040');
};
var reportAnswerBtnOnclick = function() {
    doReport($(this).attr('report-id'),'answer','502');
};

var doReport = function(id,type,reason) {
    $.ajax({
        type : 'POST',
        url : 'http://www.zhihu.com/report',
        data : {
            reason : reason,
            detail : '',
            type : type,
            id : id,
            _xsrf : batch_report_xsrf
        },
        success : function() {
            $('a[report-id='+id+']').replaceWith(function() { return '<span class=zg-link-gray>已举报</span>'; })
            .unbind('click', reportAnswerBtnOnclick)
            .unbind('click', reportQuestionBtnOnclick);
        }
    });
};

var addReportBtn = function (item) {
    console.log(item.find('.report-added').length);
    if (item.find('.report-added').length != 0) {
        return;
    }
    item.addClass('report-added');
    
    var qid = item.find('a[data-follow="q:link"]').attr('id').split('-')[1];
    var qr_href = $('<a>举报问题（广告）</a>').attr('class','meta-item zg-follow')
    .attr('report-id',qid)
    .attr('href','#')
    .click(reportQuestionBtnOnclick);
    item.find('div.meta').append(qr_href);
    
    var answer = item.find('a.zg-inline-block');
    if (answer.length > 0) {
        var aid = answer.attr('href').split('#')[1].split('-')[1];
        var ar_href = $('<a>举报回答（广告)</a>').attr('class', 'zg-inline-block')
        .attr('href','#')
        .attr('report-id',aid)
        .click(reportAnswerBtnOnclick);
        item.find('div.question-content').append(ar_href);
    }
};

var loadBatchReportAnswerPage = function () {
    var list = $('.zm-search3-item.question').not('.report-added');
    for (var i = 0; i < list.length; i++) {
        addReportBtn($(list[i]));
    }
};

var dynamicLoad = function(event) {
    alert(event.target);
};

loadBatchReportAnswerPage();

MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
var observer = new MutationObserver(function(mutations, observer) {
    loadBatchReportAnswerPage();
});

observer.observe(document.getElementsByClassName('zh-general-list clearfix')[0], {
    subtree: true,
    
    childList: true,
});
