# Copyright (c) 2022 pikkarin
# This software is released under the MIT License, see LICENSE.

import argparse
import os

import geopandas as gpd
from shapely.geometry import box
from tqdm import tqdm
import numpy as np


def get_original_xy(kukaku: str) -> tuple[int, int]:
    """区画北西端のX, Y座標を求める

    Args:
        kukaku (str): 公共測量標準図式 第1節 総則 第84条の4の一で定義される区画名。

    Returns:
        tuple[int, int]: 区画北西端のX, Y座標
    """
    str_y = kukaku[0]
    str_x = kukaku[1]

    # シフトさせる区画数を求める
    shift_y = ord(str_y) - 65
    shift_x = ord(str_x) - 65

    # 区画北西端のX, Y座標を求める
    original_y = (300 - shift_y * 30) * 1000
    original_x = (-160 + shift_x * 40) * 1000

    return original_x, original_y


def make_code(zone: int, kukaku: str, x: int, y: int, i_x: int, i_y: int, level: int) -> str:
    """対応する地図情報レベルの図郭番号を求める

    Args:
        zone (int): 平面直角座標系の系番号
        kukaku (str): 地図情報レベル50000の図郭コード
        x (int): 地図情報レベル5000のX軸
        y (int): 地図情報レベル5000のY軸
        i_x (int): 地図情報レベル2500以下のX軸
        i_y (int): 地図情報レベル2500以下のY軸
        level (int): 求める地図情報レベル

    Returns:
        str: 図郭番号
    """
    # 地図情報レベル5000の場合の分割番号
    code_lev5000 = '{:02}'.format(zone) + kukaku + str(y) + str(x)
    if level == 5000:
        return code_lev5000
    # 地図情報レベル2500の場合
    elif level == 2500:
        block = (2 * i_y + i_x) + 1
        code_lev2500 = code_lev5000 + str(block)
        return code_lev2500
    # 地図情報レベル1250相当の場合
    elif level == 1250:
        block = str(i_y + 1) + str(i_x + 1)
        code_lev1250 = code_lev5000 + block
        return code_lev1250
    # 地図情報レベル1000の場合
    elif level == 1000:
        block = str(i_y) + chr(65 + i_x)
        code_lev1000 = code_lev5000 + block
        return code_lev1000
    # 地図情報レベル500の場合
    elif level == 500:
        block = str(i_y) + str(i_x)
        code_lev500 = code_lev5000 + block
        return code_lev500
    # 地図情報レベル250の場合
    elif level == 250:
        block = chr(65 + i_y) + chr(65 + i_x)
        code_lev250 = code_lev5000 + block
        return code_lev250


def make_kukaku(zone: int, kukaku: str, level: int) -> list:
    """区画内の図郭の四隅座標と図郭番号を求める

    Args:
        zone (int): 平面直角座標系の系番号
        kukaku (str): 公共測量標準図式 第1節 総則 第84条の4の一で定義される区画名。
        level (int): 求める地図情報レベル

    Returns:
        list: 四隅座標から求めたポリゴンのリストとその図郭番号リスト
    """
    code_list = []  # 図郭番号
    geometry_list = []

    # 区画北西端のX, Y座標を取得
    original_x, original_y = get_original_xy(kukaku)

    # 地図情報レベル5000の図郭の東西幅[m]および南北幅[m]
    dx_lev5000 = 4000
    dy_lev5000 = 3000

    # 地図情報レベル5000からの分割数
    div_x = int(5000 / level)
    div_y = int(5000 / level)
    # 出力する地図情報レベルの図郭の東西幅[m]および南北幅[m]
    dx = int(dx_lev5000 / div_x)
    dy = int(dy_lev5000 / div_y)

    # 1区画を南北10等分、東西10等分
    for y in range(10):
        for x in range(10):
            # 地図情報レベル5000の北西端座標
            lev5000_original_x = original_x + x * dx_lev5000
            lev5000_original_y = original_y - y * dy_lev5000
            # 出力する地図情報レベルの四隅の座標を求める
            for i_y in range(div_y):
                y_n = lev5000_original_y - i_y * dy  # 北端
                y_s = lev5000_original_y - (i_y + 1) * dy  # 南端
                min_y, max_y = sorted([y_n, y_s])
                for i_x in range(div_x):
                    x_w = lev5000_original_x + i_x * dx  # 西端
                    x_e = lev5000_original_x + (i_x + 1) * dx  # 東端
                    min_x, max_x = sorted([x_w, x_e])
                    geometry_list.append(box(min_x, min_y, max_x, max_y))
                    code_list.append(make_code(zone, kukaku, x, y, i_x, i_y, level))

    return code_list, geometry_list


def make_grid(zone: int, level: int) -> None:
    """指定した平面直角座標系にて指定した地図情報レベルの国土基本図の図郭を作成

    Args:
        zone (int): 平面直角座標系の系番号
        level (int): 地図情報レベル
    """
    grid_gdf = gpd.GeoDataFrame([])

    code_list = []
    geometry_list = []

    num_kuiki_y = 20
    # 9系の場合、伊豆諸島まで含むので図郭割をZHまで生成
    if zone == 9:
        num_kuiki_y = 26
    num_kuiki_x = 8
    num_kuiki = num_kuiki_y * num_kuiki_x

    pbar = tqdm(range(num_kuiki))
    for kuiki_y in range(num_kuiki_y):
        for kuiki_x in range(num_kuiki_x):
            kukaku = chr(65 + kuiki_y) + chr(65 + kuiki_x)
            per_code_list, per_geometry_list = make_kukaku(zone, kukaku, level)
            code_list.extend(per_code_list)
            geometry_list.extend(per_geometry_list)
            pbar.update()
    pbar.close()

    grid_gdf['code'] = code_list
    grid_gdf['geometry'] = geometry_list

    return grid_gdf


def selected_land_area_grid(grid_gdf: gpd.GeoDataFrame, zone_land_area_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """生成した国土基本図の図郭

    Args:
        grid_gdf (gpd.GeoDataFrame): _description_
        zone_land_area_gdf (gpd.GeoDataFrame): _description_

    Returns:
        gpd.GeoDataFrame: _description_
    """
    inp, _ = zone_land_area_gdf.sindex.query_bulk(grid_gdf.geometry, predicate='intersects')
    grid_gdf['intersects'] = np.isin(np.arange(0, len(grid_gdf)), inp)
    land_area_grid_gdf = grid_gdf[grid_gdf['intersects']].reset_index(drop=True)

    return land_area_grid_gdf


def write_gdf(grid_gdf: gpd.GeoDataFrame, zone: int, level: int, save_dir: str) -> None:
    """GeoDataFrameをGeoJSON形式で書き出す

    Args:
        grid_gdf (gpd.GeoDataFrame): 書き出すGeoDataframe
        zone (int): 書き出す図郭の平面直角座標系の系
        level (int): 書き出す図郭の地図情報レベル
        save_dir (str): 保存先のディレクトリのパス
    """
    epsg = 6668 + zone
    grid_gdf.set_crs(epsg=epsg, inplace=True)
    filename = 'Zone{}_level{}.shp'.format(zone, level)
    save_path = os.path.join(save_dir, filename)

    grid_gdf.to_file(save_path)


def main():
    # set arguments
    parser = argparse.ArgumentParser(description='国土基本図の図郭のシェープファイルを作成')
    parser.add_argument('zone', type=int, help="(int) 作成したい平面直角座標系の系番号")
    parser.add_argument('level', choices=[5000, 2500, 1250, 1000, 500, 250], type=int, help="(int) 作成したい図郭の地図情報レベル")
    parser.add_argument('save_dir', type=str, help="(str) 保存するディレクトリのパス")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    # 系番号で分割したベクターデータを読み込む
    japanese_zone_gdf = gpd.read_file('./data/jgd_latlon2rect_6668.shp')

    # 図郭を生成したい系番号の領域だけ抽出
    zone_gdf = japanese_zone_gdf[japanese_zone_gdf['Zone'] == args.zone]
    zone_gdf = zone_gdf.to_crs(epsg=int(zone_gdf['JGD2011']))

    # 国土基本図の図郭のGeoDataFrameを作成
    grid_gdf = make_grid(args.zone, args.level)

    # 生成した国土基本図の図郭のうち、陸地がある箇所のみを抽出
    land_area_grid_gdf = selected_land_area_grid(grid_gdf, zone_gdf)

    # 生成した図郭をESRI Shapefile形式で書き出す
    write_gdf(land_area_grid_gdf, args.zone, args.level, args.save_dir)


if __name__ == "__main__":
    main()
