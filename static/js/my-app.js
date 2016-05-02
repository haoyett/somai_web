// Initialize your app
var myApp = new Framework7();

// Export selectors engine
var $$ = Dom7;

// 加载flag
var loading = false;
var loadingUsers = false;
var loadingPhotos = false;

// 上次加载的序号
var lastPage = 1;
var lastPageUsers = 1;
var lastPagePhotos = 1;

// 每次请求的数量
var perPageSize = 20;

// 搜索关键词
var search_query = ''; 

var filterTypeConfig = {
    'user': '姓名',
    'company': '公司',
    'school': '学校',
    'position': '职位',
}


// Add view
var mainView = myApp.addView('.view-main', {
    // Because we use fixed-through navbar we can enable dynamic navbar
    dynamicNavbar: true,
    domCache: true
});


// 搜索栏设置
var mySearchbar = myApp.searchbar('.searchbar', {
    onEnable: function(s){

    },
    onDisable: function(s){
       clearSearchbar();
    },
    onSearch: function(s){
        search_query = s.query;
        var filterType = $$('.searchbar-filter-ac').attr('data-filter');

        // user查询姓名，直接搜索
        // 其余，需要按下Enter按键才发送搜索请求
        if (filterType == 'user') {
            // 没有关键词，清除搜索区
            if (search_query == '' || search_query == undefined) {
                clearSearchbar();
                return;
            };

            // 加载搜索结果
            searchFirstLoad();
        } else {
            clearSearchbar();
        }

    },
    onClear: function(s){
        clearSearchbar();
    },

    customSearch: true, 
});



// 首页-快速搜索链接
$$('.search-href').on('click', function(){
    searchLinkClick(this);
});


// 首页-搜索栏筛选
$$('.searchbar-filter-ac').on('click', function () {
    searchFilterClick(this);
});

function indexPageInit()
{
}



// index页面初始化
myApp.onPageInit('index', function (page) {

    mySearchbar = myApp.searchbar('.searchbar', {
        onEnable: function(s){

        },
        onDisable: function(s){
           clearSearchbar();
        },
        onSearch: function(s){
            console.log('onSearch' + s.query);

            search_query = s.query;
            var filterType = $$('.searchbar-filter-ac').attr('data-filter');

            // user查询姓名，直接搜索
            // 其余，需要按下Enter按键才发送搜索请求
            if (filterType == 'user') {
                // 没有关键词，清除搜索区
                if (search_query == '' || search_query == undefined) {
                    clearSearchbar();
                    return;
                };

                // 加载搜索结果
                // searchFirstLoad();
            } else {
                clearSearchbar();
            }

        },
        onClear: function(s){
            clearSearchbar();
        },

        customSearch: true, 
    });

    // 首页-快速搜索链接
    $$('.search-href').on('click', function(){
        searchLinkClick(this);
    });

    // 搜索栏筛选
    $$('.searchbar-filter-ac').on('click', function () {
        searchFilterClick(this);
    });
    
});


// user页面初始化
myApp.onPageInit('user', function (page) {

    // 点击头像处理
    var img = $$(".item-photo img");
    img.on('click', function (event) {
        smallSrc = img.attr('src');

        var myPhotoBrowser = myApp.photoBrowser({
            photos: [smallSrc],
            expositionHideCaptions: true,
            theme: 'dark',
            navbar: false,
            toolbar: false,
            swipeToClose: false,
            onTap: function(){
                myPhotoBrowser.close();
            },
        });   
        myPhotoBrowser.open(); // 打开图片浏览器
    });

});


// photos页面初始化
myApp.onPageInit('photos', function (page) {

    attachLoader('.infinite-scroll-photos');
    lastPagePhotos = 1;

    $$('.infinite-scroll-photos').on('infinite', function () {
        // 如果正在加载，则退出
        if (loadingPhotos) return;

        // 设置flag
        loadingPhotos = true;

        var params = {
            gender: 2,
            _display: 'json',
            page: lastPagePhotos
        };

        $$.getJSON('/photos', params, function (json) {

            // 重置加载flag
            loadingPhotos = false;
            
            if (json.code == 200) {
                // if (json.data.photos.length < perPageSize) {
                //     detachLoader('.infinite-scroll-photos');
                //     return;
                // };
            
                // 生成新条目的HTML
                var data = json.data.photos;
                var html = '';
                for (var i in data) {
                     html += '<li>' + 
                                '<a href="user?id=' + data[i]['id'] + '">' +
                                '<div class="item-content">' + 
                                    '<div class="item-media"><img src="' + data[i]['avatar'] + '" width="160"></div>' + 
                                    '<div class="item-inner">' +
                                        '<div class="item-title-row">' +
                                            '<div class="item-title">' + data[i]['name'] + ' | ' + data[i]['position'] + '</div>' +  
                                        '</div>' + 
                                    '</div>' + 
                                '</div>' + 
                                '</a>' +
                            '</li>';
                };

                // 添加新条目
                $$('.list-group-photos ul').append(html);
                
                // 更新最后加载的序号
                lastPagePhotos += 1;
            } else{  
                detachLoader('.infinite-scroll-photos');
                myApp.alert(json.msg);
                return;
            }
        });
    });
});

// // 离开 users 页面 
// myApp.onPageBeforeRemove('users', function(page){
//     // 隐藏/index页面的加载图标
//     showLoader('.infinite-scroll');
// });



// 判断按键
function keyUp(e) {
    var currKey = 0;
    var e = e || event;
    currKey = e.keyCode || e.which || e.charCode;

    var filterType = $$('.searchbar-filter-ac').attr('data-filter');

    // Enter按键.
    if (currKey == 13 && filterType != 'user') {
        loadSearchLayer();
    };
    // var keyName = String.fromCharCode(currKey);
    // alert("按键码: " + currKey + " 字符: " + keyName);
}
document.onkeyup = keyUp;


// 首页-快速搜索链接
function searchLinkClick(obj)
{
    var type = $$(obj).attr('data-type');
    var q = $$(obj).attr('data-q');

    $$('.searchbar-filter-ac').attr('data-filter', type);
    $$('.searchbar-filter-ac').html(filterTypeConfig[type]);

    console.log(mySearchbar);
    mySearchbar.search(q);
    searchFirstLoad();
}

// 搜索栏筛选
function searchFilterClick(obj){
    var target = obj;
    var buttons = [
        {
            text: '筛选',
            label: true
        },
        {
            text: filterTypeConfig.user,
            onClick: function () {
                $$(target).text(filterTypeConfig.user);
                $$(target).attr('data-filter', 'user');
            }
        },
        {
            text: filterTypeConfig.company,
            onClick: function () {
                $$(target).text(filterTypeConfig.company);
                $$(target).attr('data-filter', 'company');
            }
        },
        {
            text: filterTypeConfig.school,
            onClick: function () {
                $$(target).text(filterTypeConfig.school);
                $$(target).attr('data-filter', 'school');
            }
        },
        {
            text: filterTypeConfig.position,
            onClick: function () {
                $$(target).text(filterTypeConfig.position);
                $$(target).attr('data-filter', 'position');
            }
        },
    ];
    myApp.actions(target, buttons);
}

// 还原搜索栏
function clearSearchbar() {
    $$('.search-page').html('');
    $$('.index-page').show();

    lastPage = 0;
    detachLoader('.infinite-scroll-search');
}
// 搜索弹层
function loadSearchLayer () {

    var filterType = $$('.searchbar-filter-ac').attr('data-filter');

    params = {
        'q': search_query,
        'type': filterType,
        '_display': 'json',
    }
    $$.getJSON('/search_suggest', params, function (json) {
        if (json.code == 200) {

            var data = json.data.list;
            if (data.length == 0) {
                return;
            }

            var target = $$('.searchbar');
            var buttons = [
                {
                    text: '请选择以下关键词',
                    label: true
                },
            ];
            if (data.indexOf(search_query) == -1) {
                buttons.push({
                    'text': search_query,
                    onClick: function (e) {
                        mySearchbar.search(this.text);
                        searchFirstLoad();
                    }
                });
            };


            for (var i in data) {
                var item = {
                    'text': data[i],
                    onClick: function (e) {
                        mySearchbar.search(this.text);
                        searchFirstLoad();
                    }
                }
                buttons.push(item);
            }
            buttons.push({
                text: 'Cancel',
                color: 'red'
            });
            myApp.actions(target, buttons);

            // 加载弹层后，让input失去焦点，收起键盘。
            $$('.searchbar input').blur();

        } else {  
            myApp.alert(json.msg);
            return;
        }
    });
}


// 首页搜索 - 首次加载
function searchFirstLoad () {

    // 显示搜索区
    $$('.index-page').hide();
    $$('.search-page').show();
    
    // 初始化 无限加载
    lastPage = 1;
    attachLoader('.infinite-scroll-search');
    $$('.infinite-scroll-search').on('infinite', searchLoop);


    var filterType = $$('.searchbar-filter-ac').attr('data-filter');

    params = {
        'q': search_query,
        'type': filterType,
        'page': 0,
        'page_size': perPageSize,
        '_display': 'json',
    }
    $$.getJSON('/search', params, function (json) {

        if (json.code == 200) {

            // 生成新条目的HTML
            var data = json.data.users;
            var total = json.data.total_found;
            var time = json.data.time;

            var html = '' +
                '<div class="list-block contacts-block contacts-list list-block-search searchbar-found">' +
                '   <div class="list-group list-group-users">' +
                '       <ul>';
            html += '' +
                '<li>' + 
                '       <div class="item-content">' +
                '           <div class="item-inner">' +
                '               <div class="item-title-row">' +
                '                   <div class="item-title">'+ 
                '                       <span class="item-title-small">查询到 ' + total + ' 条结果</span>' +
                '                   </div>' +
                '               </div>' +
                '               <div class="item-title-small"><span>耗时 ' + time + ' s</span></div>'
                '           </div>' +
                '       </div>' + 
                '</li>';  

            for (var i in data) {
                html += '' +
                    '<li>' + 
                    '   <a href="user?id=' + data[i]['id'] + '">' +
                    '       <div class="item-content">' +
                    '           <div class="item-media"><img src="' + data[i]['avatar'] + '" width="100"></div>' +
                    '           <div class="item-inner">' +
                    '               <div class="item-title-row">' +
                    '                   <div class="item-title">' + data[i]['name'] + 
                    '                       <span class="item-title-small">' + data[i]['company_name'] + ' ' + data[i]['position'] + '</span>' +
                    '                   </div>' +
                    '                   <div class="item-subtitle">' + data[i]['trade'] + ' | ' + data[i]['school'] + '</div>' +
                    '               </div>' +
                    '               <div class="item-after"><span class="badge badge-power">P: ' + data[i]['rank'] + '</span></div>'
                    '           </div>' +
                    '       </div>' + 
                    '   </a>' +
                    '</li>';
            };

            html += '' +
                '       </ul>' + 
                '   </div>' +
                '   <!-- 加载提示符 -->' +
                '   <div class="infinite-scroll-preloader infinite-scroll-search-preloader">' +
                '       <div class="preloader"></div>' +
                '   </div>' +
                '</div>';

            // 添加新条目
            $$('.search-page').html(html);

            // 隐藏加载提示符
            if (data.length < perPageSize) {
                hideLoader('.infinite-scroll-search');
                // detachLoader('.infinite-scroll-search');
            }
        }
    });
}


// 首页搜索
function searchLoop () {

    // 如果正在加载，则退出
    if (loading) return;
 
    // 设置flag
    loading = true;


    var fitlerType = $$('.searchbar-filter-ac').attr('data-filter');
    params = {
        'q': search_query,
        'type': fitlerType,
        'page': lastPage,
        'page_size': perPageSize,
        '_display': 'json',
    }
    $$.getJSON('/search', params, function (json) {
        // 重置加载flag
        loading = false;

        if (json.code == 200) {
            if (json.data.length == 0) {
                hideLoader('.infinite-scroll-search');
                return;
            };

            // 生成新条目的HTML
            var data = json.data.users;

            var html = '';
            for (var i in data) {
                html += '' +
                    '<li>' + 
                    '   <a href="user?id=' + data[i]['id'] + '">' +
                    '       <div class="item-content">' +
                    '           <div class="item-media"><img src="' + data[i]['avatar'] + '" width="100"></div>' +
                    '           <div class="item-inner">' +
                    '               <div class="item-title-row">' +
                    '                   <div class="item-title">' + data[i]['name'] + 
                    '                       <span class="item-title-small">' + data[i]['company_name'] + ' ' + data[i]['position'] + '</span>' +
                    '                   </div>' +
                    '                   <div class="item-subtitle">' + data[i]['trade'] + ' | ' + data[i]['school'] + '</div>' +
                    '               </div>' +
                    '               <div class="item-after"><span class="badge badge-power">P: ' + data[i]['rank'] + '</span></div>'
                    '           </div>' +
                    '       </div>' + 
                    '   </a>' +
                    '</li>';
            };

            // 添加新条目
            $$('.search-page ul').append(html);

            // 隐藏加载提示符
            if (data.length < perPageSize) {
                hideLoader('.infinite-scroll-search');
            }

            // 更新最后加载的序号
            lastPage += 1;
        } else {  
            hideLoader('.infinite-scroll-search');
            myApp.alert(json.msg);
            return;
        }
    });
}

/**
 * 清除加载事件
 */
function detachLoader(className)
{
    // 加载完毕，则注销无限加载事件，以防不必要的加载
    myApp.detachInfiniteScroll($$(className));
    // 删除加载提示符
    $$(className + '-preloader').hide();
}

/**
 * 添加加载事件
 */
function attachLoader(className)
{
    r = myApp.attachInfiniteScroll($$(className));
    $$(className + '-preloader').show();
}

/**
 * 清除加载图表
 */
function hideLoader(className)
{
    // 删除加载提示符
    $$(className + '-preloader').hide();
}

/**
 * 显示加载图表
 */
function showLoader(className)
{
    // 删除加载提示符
    $$(className + '-preloader').show();
}
