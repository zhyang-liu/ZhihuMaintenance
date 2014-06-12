// ==UserScript==
// @name       ZhihuUserLogPageQuickRevert
// @namespace  http://lzy.in/
// @version    0.1
// @description  Nothing is useful.
// @match      http://www.zhihu.com/people/*/logs
// @copyright  2014+, 知乎 @刘中阳
// ==/UserScript==

var quickRevertBtnOnClick = function(item) {
    var id = $(this).attr('revert-id');
    console.log(id);
    $.ajax({
        type : 'POST',
        url : 'http://www.zhihu.com/revert',
        data : {
            revision: id,
            reason : $('input#quick-revert-reason').val(),
            _xsrf : $('input[name="_xsrf"]').attr('value')
        },
        success : function(data) {
            console.log(data);
            $('a[revert-id='+id+']').replaceWith(function() { return '<span class=zg-link-gray>已撤销，刷新查看状态。</span>'; })
                                    .unbind('click', quickRevertBtnOnClick);
        }
    });
};

var addQuickRevertButtons = function () {
    var list = $('div#zh-profile-log-list div.zm-item').not('.oneclick-added');
    for (var i = 0; i < list.length; i++) {
        var log_id = list[i]['id'].split('-')[1];
        $(list[i]).addClass('oneclick-added')
                  .find('a[name="revert"]')
                  .after($('<a>快速撤销</a>')
                          .attr('class','meta-item zg-follow')
                          .attr('revert-id',log_id)
                          .attr('href','#')
                          .click(quickRevertBtnOnClick))
                  .after('<span class="zg-bull">•</span>');
    }
};

// run once
$('span.zm-profile-section-name').append('，撤销理由：<input type="text" class="zg-form-text-input" id="quick-revert-reason" value="撤销广告编辑" />')
addQuickRevertButtons();
MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
var observer = new MutationObserver(function(mutations, observer) {
    addQuickRevertButtons();
});

observer.observe(document.getElementById('zh-profile-log-list'), {
    subtree: true,
    childList: true,
});