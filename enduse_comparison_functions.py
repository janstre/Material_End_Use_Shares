import pandas as pd
import re


def create_two_way_correspondences(correspondences, first_key="GLORIA END_USES", second_key="EXIOBASE END_USES"):
    correspondence_first_key = {}
    correspondence_second_key = {}
    equal_names = {}

    for correspondence_dict in correspondences:
        end_use_gloria = correspondence_dict[first_key]
        end_use_exio = correspondence_dict[second_key]
        if end_use_gloria == end_use_exio:
            equal_names[end_use_gloria] = end_use_exio
            continue
        if end_use_gloria in correspondence_first_key:
            correspondence_first_key[end_use_gloria].append(end_use_exio)
        else:
            correspondence_first_key[end_use_gloria] = [end_use_exio]

        if end_use_exio in correspondence_second_key:
            correspondence_second_key[end_use_exio].append(end_use_gloria)
        else:
            correspondence_second_key[end_use_exio] = [end_use_gloria]

    return_dict = {first_key: correspondence_first_key, second_key: correspondence_second_key, "equal": equal_names}
    return return_dict


def combine_enduse_from_csv(csv_files):
    enduse_dfs = []
    for csv_file in csv_files:
        country_name = re.search(r"_([^_]+)\.csv", csv_file).group(1)
        year = re.search(r"(\d{4})", csv_file).group()
        df = pd.read_csv(csv_file)
        df["country"] = country_name
        df["year"] = year
        enduse_dfs.append(df)
    all_enduses = pd.concat(enduse_dfs)

    return all_enduses


def map_gloria_to_exio_enduses(all_enduses, correspondence_gloria_to_exio):
    all_enduses_mapped = all_enduses.copy()

    for gloria_enduse, exio_enduse_list in correspondence_gloria_to_exio.items():
        if len(exio_enduse_list) > 1:
            new_column_name = ','.join(exio_enduse_list)
        if len(exio_enduse_list) == 1:
            new_column_name = exio_enduse_list[0]

        if new_column_name not in all_enduses_mapped.columns:
            all_enduses_mapped = all_enduses_mapped.rename(columns={gloria_enduse: new_column_name})
            print(f"Renamed {gloria_enduse} to {new_column_name}")
        else:
            all_enduses_mapped[new_column_name] += all_enduses_mapped[gloria_enduse]
            all_enduses_mapped = all_enduses_mapped.drop(columns=gloria_enduse)
    # error in this mapping function?

    return all_enduses_mapped


def create_enduse_by_country(all_enduses, gloria_exiobase_correspondence):
    country_material_enduse = {}
    for country in all_enduses.groupby("country"):
        country_material_enduse[country[0]] = {}
        for material in country[1].groupby("MISO_material"):
            country_material_enduse[country[0]][material[0]] = []
            for enduse in set(gloria_exiobase_correspondence["GLORIA END_USES"]):
                pivoted = pd.pivot(material[1][[enduse, "year"]], columns="year", values=enduse)
                pivoted["Enduse"] = enduse
                pivoted = pivoted.set_index("Enduse")
                country_material_enduse[country[0]][material[0]].append(pivoted)
            country_material_enduse[country[0]][material[0]] = pd.concat(country_material_enduse[country[0]][material[0]])
    # here is a sum missing?
    return country_material_enduse


def check_enduse_integrity(country_material_enduse):
    invalids = {}
    for country, df_dict in country_material_enduse.items():
        for material, df in df_dict.items():
            sum_test = df.sum(axis=0)
            below_100 = sum_test[sum_test < 99.999]
            if len(below_100) > 0:
                print(f"Enduses below 100 in {country} {material}")
                invalids[(country, material)] = below_100
            above_100 = sum_test[sum_test > 100.001]
            if len(above_100) > 0:
                print(f"Enduses above 100 in {country} {material}")
                invalids[(country, material)] = above_100
    return invalids


def transform_gloria_dict_to_df(country_dict, country_correspondences):

    total_df = []
    for country_filename, material_dict in country_dict.items():
        country_df = []
        for list_entry in country_correspondences.to_dict(orient="records"):
            if list_entry["GLORIA_filenames"] == country_filename:
                for material, df in material_dict.items():
                    df["MISO2_country"] = list_entry["MISO2_country"]
                    df["Code ISO3166-1"] = list_entry["Code ISO3166-1"]
                    df["MISO2_Material"] = material
                    country_df.append(df)
        country_df = pd.concat(country_df)
        total_df.append(country_df)
    assert len(country_dict.keys()) == len(total_df)

    return pd.concat(total_df).reset_index().set_index(["MISO2_country", "Code ISO3166-1", "Enduse", "MISO2_Material"])

