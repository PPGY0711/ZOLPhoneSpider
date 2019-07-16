# -*- coding:utf-8 -*-

from pymongo import MongoClient
from gridfs import *
import os

if __name__ == '__main__':
    # 品牌名称对应字典
    name2brand = {
        r'logos\12Ke_logo.png':'21克.png',
        r'logos\360_logo.png':'360.png',
        'logos\8848_logo.png':'8848.png',
        'logos\AGM_logo.png':'AGM.png',
        'logos\Alcatel_logo.png':'阿尔卡特.png',
        'logos\Angelcare_logo.png':'守护宝.png',
        'logos\Antone_logo.png':'Ant one.png',
        'logos\Apple_logo.png':'苹果.png',
        'logos\ASUS_logo.png':'华硕.png',
        'logos\Atman_logo.png':'创星.png',
        'logos\Banghua_logo.png': '邦华.png',
        'logos\Bihee_logo.png': '百合.png',
        'logos\Biojuet_logo.png': '铂爵.png',
        'logos\Bird_logo.png':'波导.png',
        'logos\CAPPU.png':'卡布奇诺.png',
        'logos\Changhong_logo.png': '长虹.png',
        'logos\ChinaMobile_logo.png':'中国移动.png',
        'logos\Comio_logo.png':'卡美欧.png',
        'logos\Conquer_logo.png':'征服.png',
        'logos\Coolpad_logo.png': '酷派.png',
        'logos\Dazen_logo.png':'大神.png',
        'logos\DBV_logo.png':'DBV.png',
        'logos\Doov_logo.png':'朵唯.png',
        'logos\DTDX_logo.png':'大唐电信.png',
        'logos\Dy_logo.png':'独影天幕.png',
        'logos\EREB_logo.png':'E人E本.png',
        'logos\Gemry_logo.png':'詹姆士.png',
        'logos\Gionee_logo.png':'金立.png',
        'logos\Gome_logo.png':'国美.png',
        'logos\Google_logo.png':'谷歌.png',
        'logos\Gree_logo.png':'格力.png',
        'logos\Guangxin_logo.png':'广信.png',
        'logos\Haier_logo.png':'海尔.png',
        'logos\Hammer_logo.png':'锤子科技.png',
        'logos\Hasee_logo.png':'神舟.png',
        'logos\Heisha_logo.png':'黑鲨.png',
        'logos\Hisense_logo.png':'海信.png',
        'logos\Honor_logo.png':'荣耀.png',
        'logos\HTC_logo.png':'HTC.png',
        'logos\HUAWEI_logo.png':'华为.png',
        'logos\Huibo_logo.png':'会播.png',
        'logos\Huiwei_logo.png':'汇威.png',
        'logos\Imoo_logo.png':'imoo.png',
        'logos\Infocus_logo.png':'富可视.png',
        'logos\Innos_logo.png':'innos.png',
        'logos\ioutdoor_logo.png':'ioutdoor.png',
        'logos\Ivvi_logo.png':'ivvi.png',
        'logos\Kodak_logo.png':'柯达.png',
        'logos\Konka_logo.png':'康佳.png',
        'logos\Koobee_logo.png':'酷比.png',
        'logos\Kreta_logo.png':'克里特.png',
        'logos\Lenovo_logo.png':'联想.png',
        'logos\Meitu_logo.png':'美图.png',
        'logos\Meizu_logo.png':'魅族.png',
        'logos\Microsoft_logo.png':'微软.png',
        r'logos\Neken_logo.png':'尼凯恩.png',
        r'logos\Neolix_logo.png':'新石器.png',
        r'logos\Newman_logo.png':'纽曼.png',
        r'logos\Nokia_logo.png':'诺基亚.png',
        r'logos\Nuoio_logo.png':'努比亚.png',
        'logos\Oinom_logo.png':'乐目.png',
        'logos\Oneplus_logo.png':'一加.png',
        'logos\Oppo_logo.png':'OPPO.png',
        'logos\Oukitel_logo.png':'.png',
        'logos\Philips_logo.png':'飞利浦.png',
        'logos\PPTV_logo.png':'PPTV.png',
        'logos\Qingcheng_logo.png':'青橙.png',
        'logos\Qin_logo.png':'多亲.png',
        'logos\Razer_logo.png':'雷蛇.png',
        'logos\Realme_logo.png':'realme.png',
        'logos\Redmi_logo.png':'红米.png',
        'logos\ROG_logo.png':'ROG.png',
        'logos\Royole_logo.png':'柔宇.png',
        'logos\RugGear_logo.png':'朗界.png',
        'logos\SAGA_logo.png':'传奇.png',
        'logos\Sharp_logo.png':'夏普.png',
        'logos\Shown_logo.png':'首云.png',
        'logos\Sony_logo.png':'索尼.png',
        'logos\Soyes_logo.png':'索野.png',
        'logos\Sugar_logo.png':'SUGAR.png',
        'logos\SumSung_logo.png':'三星.png',
        'logos\TCL_logo.png':'TCL.png',
        'logos\TECNO_logo.png':'传音.png',
        'logos\Tianyu_logo.png':'天语.png',
        'logos\TP_link_logo.png':'TP_LINK.png',
        'logos\Turing_logo.png':'图灵.png',
        'logos\Vaio_logo.png':'Vaio.png',
        'logos\VEB_logo.png':'VEB.png',
        'logos\Vertu_logo.png':'VERTU.png',
        'logos\Vivo_logo.png':'vivo.png',
        'logos\Xiaolajiao_logo.png':'小辣椒.png',
        'logos\Xiaomi_logo.png':'小米.png',
        'logos\Yamayahoo_logo.png':'雅马亚虎.png',
        'logos\YIbainian_logo.png':'易百年.png',
        'logos\Yota_logo.png':'Yotaphone.png',
        'logos\Yunhu_logo.png':'云狐.png',
        'logos\ZTE_logo.png':'中兴.png',
        'logos\ZUK_logo.png':'联想ZUK.png'}

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
