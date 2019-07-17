# -*- coding:utf-8 -*-

from pymongo import MongoClient
from gridfs import *
import os

if __name__ == '__main__':
    # 品牌名称对应字典
    name2brand = {
        r'logos\21Ke_logo.png': '21克.png',
        r'logos\360_logo.png': '360.png',
        r'logos\8848_logo.png': '8848.png',
        r'logos\AGM_logo.png': 'AGM.png',
        r'logos\Alcatel_logo.png': '阿尔卡特.png',
        r'logos\Angelcare_logo.png': '守护宝.png',
        r'logos\Antone_logo.png': 'Ant one.png',
        r'logos\Apple_logo.png': '苹果.png',
        r'logos\ASUS_logo.png': '华硕.png',
        r'logos\Atman_logo.png': '创星.png',
        r'logos\Banghua_logo.png': '邦华.png',
        r'logos\Bihee_logo.png': '百合.png',
        r'logos\Biojuet_logo.png': '铂爵.png',
        r'logos\Bird_logo.png': '波导.png',
        r'logos\CAPPU.png': '卡布奇诺.png',
        r'logos\Changhong_logo.png': '长虹.png',
        r'logos\ChinaMobile_logo.png': '中国移动.png',
        r'logos\Comio_logo.png': '卡美欧.png',
        r'logos\Conquer_logo.png': '征服.png',
        r'logos\Coolpad_logo.png': '酷派.png',
        r'logos\Dazen_logo.png': '大神.png',
        r'logos\DBV_logo.png': 'DBV.png',
        r'logos\Doov_logo.png': '朵唯.png',
        r'logos\DTDX_logo.png': '大唐电信.png',
        r'logos\Dy_logo.png': '独影天幕.png',
        r'logos\EREB_logo.png': 'E人E本.png',
        r'logos\Gemry_logo.png': '詹姆士.png',
        r'logos\Gionee_logo.png': '金立.png',
        r'logos\Gome_logo.png': '国美.png',
        r'logos\Google_logo.png': '谷歌.png',
        r'logos\Gree_logo.png': '格力.png',
        r'logos\Guangxin_logo.png': '广信.png',
        r'logos\Haier_logo.png': '海尔.png',
        r'logos\Hammer_logo.png': '锤子科技.png',
        r'logos\Hasee_logo.png': '神舟.png',
        r'logos\Heisha_logo.png': '黑鲨.png',
        r'logos\Hisense_logo.png': '海信.png',
        r'logos\Honor_logo.png': '荣耀.png',
        r'logos\HTC_logo.png': 'HTC.png',
        r'logos\HUAWEI_logo.png': '华为.png',
        r'logos\Huibo_logo.png': '会播.png',
        r'logos\Huiwei_logo.png': '汇威.png',
        r'logos\Imoo_logo.png': 'imoo.png',
        r'logos\Infocus_logo.png':'富可视.png',
        r'logos\Innos_logo.png': 'innos.png',
        r'logos\ioutdoor_logo.png': 'ioutdoor.png',
        r'logos\Ivvi_logo.png': 'ivvi.png',
        r'logos\Kodak_logo.png': '柯达.png',
        r'logos\Konka_logo.png': '康佳.png',
        r'logos\Koobee_logo.png': '酷比.png',
        r'logos\Kreta_logo.png': '克里特.png',
        r'logos\Lenovo_logo.png': '联想.png',
        r'logos\Meitu_logo.png': '美图.png',
        r'logos\Meizu_logo.png': '魅族.png',
        r'logos\Microsoft_logo.png': '微软.png',
        r'logos\Neken_logo.png': '尼凯恩.png',
        r'logos\Neolix_logo.png': '新石器.png',
        r'logos\Newman_logo.png': '纽曼.png',
        r'logos\Nokia_logo.png': '诺基亚.png',
        r'logos\Nuoio_logo.png': '努比亚.png',
        r'logos\Oinom_logo.png': '乐目.png',
        r'logos\Oneplus_logo.png': '一加.png',
        r'logos\Oppo_logo.png': 'OPPO.png',
        r'logos\Oukitel_logo.png': '.png',
        r'logos\Philips_logo.png': '飞利浦.png',
        r'logos\PPTV_logo.png': 'PPTV.png',
        r'logos\Qingcheng_logo.png': '青橙.png',
        r'logos\Qin_logo.png': '多亲.png',
        r'logos\Razer_logo.png': '雷蛇.png',
        r'logos\Realme_logo.png': 'realme.png',
        r'logos\Redmi_logo.png': '红米.png',
        r'logos\ROG_logo.png': 'ROG.png',
        r'logos\Royole_logo.png': '柔宇.png',
        r'logos\RugGear_logo.png': '朗界.png',
        r'logos\SAGA_logo.png': '传奇.png',
        r'logos\Sharp_logo.png': '夏普.png',
        r'logos\Shown_logo.png': '首云.png',
        r'logos\Sony_logo.png': '索尼.png',
        r'logos\Soyes_logo.png': '索野.png',
        r'logos\Sugar_logo.png': 'SUGAR.png',
        r'logos\SumSung_logo.png': '三星.png',
        r'logos\TCL_logo.png': 'TCL.png',
        r'logos\TECNO_logo.png': '传音.png',
        r'logos\Tianyu_logo.png': '天语.png',
        r'logos\TP_link_logo.png': 'TP_LINK.png',
        r'logos\Turing_logo.png': '图灵.png',
        r'logos\Vaio_logo.png': 'Vaio.png',
        r'logos\VEB_logo.png': 'VEB.png',
        r'logos\Vertu_logo.png': 'VERTU.png',
        r'logos\Vivo_logo.png': 'vivo.png',
        r'logos\Xiaolajiao_logo.png': '小辣椒.png',
        r'logos\Xiaomi_logo.png': '小米.png',
        r'logos\Yamayahoo_logo.png': '雅马亚虎.png',
        r'logos\YIbainian_logo.png': '易百年.png',
        r'logos\Yota_logo.png': 'Yotaphone.png',
        r'logos\Yunhu_logo.png': '云狐.png',
        r'logos\ZTE_logo.png': '中兴.png',
        r'logos\ZUK_logo.png': '联想ZUK.png'}

    # 链接mongodb
    client = MongoClient('118.25.188.238', 27017)
    # 取得对应的collection
    db = client['phoneYelp']
    db.authenticate('phoneYelp_rw', '123456')
    # 本地硬盘上的图片目录
    dirs = 'logos'
    # 列出目录下的所有图片
    files = os.listdir(dirs)
    # 遍历图片目录集合
    for file in files:
        # 图片的全路径
        filesname = dirs + '\\' + file
        print(filesname)
        # 分割，为了存储图片文件的格式和名称
        f = name2brand[filesname].split('.')
        # 类似于创建文件
        datatmp = open(filesname, 'rb')
        # 创建写入流
        imgput = GridFS(db)
        # 将数据写入，文件类型和名称通过前面的分割得到
        insertimg = imgput.put(datatmp, content_type=f[1], filename=f[0])
        datatmp.close()
    print("Pictures uploaded.")
