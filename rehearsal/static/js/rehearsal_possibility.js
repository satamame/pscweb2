// 以下のクラスの style が定義されていること
// .header_cell
// .data_cell

// 以下のデータを View から受け取ること
var rhsls;               // 稽古のリスト

// 出席率を色に変換
function color_for_rate(rate){
    var r = 240 - (rate * 8) ** 2 - rate * 64;
    var g = 240;
    var b = r;
    return `rgb(${r}, ${g}, ${b})`;
}

// 初期化
function init(){
    document.getElementById("mode_menu").selectedIndex = 0;
    mode = document.getElementById("mode_menu").value;
}

// 出席率を色に変換
function color_for_rate(rate){
    var r = 240 - (rate * 8) ** 2 - rate * 64;
    var g = 240;
    var b = r;
    return `rgb(${r}, ${g}, ${b})`;
}

// テーブルを描画
function draw(){
    // モードを取得
    mode = document.getElementById("mode_menu").value;
    
    // thead
    var thead = "<tr><th class=\"top_left_cell\"></th>";
    
    rhsls.forEach((rhsl) => {
        // 日付を整形
        var d = new Date(rhsl['date']);
        var dateStr = `
            ${(d.getMonth()+1).toString().padStart(2, '0')}/
            ${d.getDate().toString().padStart(2, '0')}(
            ${dowChars.charAt(d.getDay())})
        `.replace(/[\n\r]+\s*/g, '');
        
        // ヘッダを出欠グラフへのリンクにする
        link = `<a href=\"/rhsl/atnd_graph/${rhsl['id']}/\">` + dateStr + "<br>"
            + rhsl['place'] + "<br>" + rhsl['start_time'] + "-" + rhsl['end_time'];
        thead += `<th class=\"header_cell\">${link}</th>`;
    });
    
    thead += "</tr>";
    
    document.getElementById("t_header").innerHTML = thead;
    
    // モードによって使うデータを変える
    var psblty;
    switch (mode){
        case "by_chrs":
            psblty = psblty_in_chrs;
            break;
        default:
            psblty = psblty_in_chrs;
            break;
    }
    
    // 最大値
    var max = 0;
    psblty.forEach((rhsl_psblty) => {
        console.log('max per rhsl: ' + Math.max(...rhsl_psblty));
        max = Math.max(max, Math.max(...rhsl_psblty));
    });
    
    console.log('max: ' + max);
    
    // tbody
    var tbody = "";
    scns.forEach((scn, scn_idx) => {
        // シーン名のカラム
        tbody += `<tr><td class=\"scn_name_cell\">${scn['name']}</td>`;
        
        rhsls.forEach((rhsl, rhsl_idx) => {
            // 可能性の値
            var point = psblty[rhsl_idx][scn_idx];
            // スロットの色
            var color = color_for_rate(point / max);
            // セルの内容
            tbody += `<td style=\"background-color:${color}; border:solid 1px #eee;\">`;
            tbody += `${Math.round(point)}</td>\n`;
        });
        
        tbody += "</tr>\n";
    });
    
    document.getElementById("t_data").innerHTML = tbody;
}
