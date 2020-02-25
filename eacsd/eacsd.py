from collections import OrderedDict, namedtuple
import decimal
import datetime
import dateutil.parser
import re


class ValidationException(Exception):
    pass


class SurveyMethods(object):
    GNSS = 'GNSSRTK'
    TS = 'Total_station'

class ViewDirections(object):
    US = 'Upstream view'
    DS = 'Downstream view'
    VA = 'View across'

class ViewDirectionsShort(object):
    US = 'US'
    DS = 'DS'
    VA = 'VA'

def parse_group(group):
    group_dict = OrderedDict(line.split('=') for line in group.split('\n'))
    return group_dict


def parse_photo_group(group):
    photos = [line.split(',') for line in group.split('\n')[1:]]
    photo_list = []
    for photo in photos:
        easting, northing, bearing, filename, remark = photo
        direction, extra = re.search(r'({}|{}|{}) ?(.*)'.format(ViewDirections.US, ViewDirections.DS, ViewDirections.VA), remark).group(1, 2)
        photo_obj = Photo(float(easting), float(northing), float(bearing), filename, direction, extra)
        photo_list.append(photo_obj)
    return photo_list

def parse_eacsd(file_obj):

    for group in file_obj.read().split('\n*\n'):
        group_type = group.split('\n')[0].split('=')[-1]
        if group.endswith('\n*'):
            group = group.replace('\n*', '')
        if group_type == EACSD.group_name:
            group_data = parse_group(group)
            eacsd_obj = EACSD(*[group_data[tag] for tag in EACSD.tags])

        elif group_type == CrossSectionHeaderGroup.group_name:
            group_data = parse_group(group)
            xs_header = CrossSectionHeaderGroup(*[group_data[tag] for tag in CrossSectionHeaderGroup.tags])
            eacsd_obj.add_cross_section(xs_header)
        elif group_type == CrossSectionAlignmentGroup.group_name:
            group_data = CrossSectionAlignmentGroup(group)
            xs_header.add_group(group_data)
        elif group_type == CrossSectionGroup.group_name:
            group_data = CrossSectionGroup(group)
            xs_header.add_group(group_data)
        elif group_type == BridgeStructureGroup.group_name:
            group_data = BridgeStructureGroup(group)
            xs_header.add_group(group_data)
        elif group_type == WeirStructureGroup.group_name:
            group_data = WeirStructureGroup(group)
            xs_header.add_group(group_data)
        elif group_type == CulvertStructureGroup.group_name:
            group_data = CulvertStructureGroup(group)
            xs_header.add_group(group_data)
        elif group_type == PhotoGroup.group_name:
            group_data = parse_photo_group(group)
            xs_header.photo_group = PhotoGroup(group_data)
        elif group_type == CentreLineStringGroup.group_name:
            eacsd_obj.add_group(CentreLineStringGroup(group))
        elif group_type == LongSectionGroup.group_name:
            eacsd_obj.add_group(LongSectionGroup(group))
        elif group_type == GeneralPhotoGroup.group_name:
            eacsd_obj.add_group(GeneralPhotoGroup(group))
        elif group_type == LongSectionLeftBankGroup.group_name:
            eacsd_obj.add_group(LongSectionLeftBankGroup(group))
        elif group_type == LongSectionRightBankGroup.group_name:
            eacsd_obj.add_group(LongSectionRightBankGroup(group))
        elif group_type == LongSectionDeepestBedGroup.group_name:
            eacsd_obj.add_group(LongSectionDeepestBedGroup(group))
        elif group_type == LongSectionDefenceLeftGroup.group_name:
            eacsd_obj.add_group(LongSectionDefenceLeftGroup(group))
        elif group_type == LongSectionDefenceRightGroup.group_name:
            eacsd_obj.add_group(LongSectionDefenceRightGroup(group))
        elif group_type == LongSectionOtherFeatureGroup.group_name:
            eacsd_obj.add_group(LongSectionOtherFeatureGroup(group))
        elif group_type == GeneralPhotographsGroup.group_name:
            eacsd_obj.add_group(GeneralPhotographsGroup(group))
        elif group_type == '':
            continue
        else:
            raise ValidationException('Group \'{}\' not recognised'.format(group_type))

    return eacsd_obj


class Group(object):
    def __init__(self, group):
        self.group = group

    def format_write(self):
        return self.group

class CrossSectionAlignmentGroup(Group):
    group_name = 'Cross-section_Alignment'
    def __init__(self, group):
        super().__init__(group)

class CrossSectionGroup(Group):
    group_name = 'Cross-section_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class BridgeStructureGroup(Group):
    group_name = 'Bridge-structure_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class WeirStructureGroup(Group):
    group_name = 'Weir-structure_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class CulvertStructureGroup(Group):
    group_name = 'Culvert-structure_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class CentreLineStringGroup(Group):
    group_name = 'Centre-line_String'
    def __init__(self, group):
        super().__init__(group)

class LongSectionGroup(Group):
    group_name = 'Long-section_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class GeneralPhotoGroup(Group):
    group_name = 'General_photographs'
    def __init__(self, group):
        super().__init__(group)

class LongSectionLeftBankGroup(Group):
    group_name = 'Long-section_Left-bank_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class LongSectionRightBankGroup(Group):
    group_name = 'Long-section_Right-bank_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class LongSectionDeepestBedGroup(Group):
    group_name = 'Long-section_Deepest-bed_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class LongSectionDefenceLeftGroup(Group):
    group_name = 'Long-section_Defence-left_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class LongSectionDefenceRightGroup(Group):
    group_name = 'Long-section_Defence-right_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class LongSectionOtherFeatureGroup(Group):
    group_name = 'Long-section_Other-feature_Data_Points'
    def __init__(self, group):
        super().__init__(group)

class GeneralPhotographsGroup(Group):
    group_name = 'General_photographs'
    def __init__(self, group):
        super().__init__(group)


class PhotoGroup(object):
    group_name = 'Cross-section_photos'

    def __init__(self, photos):
        self.ds = []
        self.us = []
        self.va = []

        for p in photos:
            if p.direction == ViewDirections.DS:
                self.ds.append(p)
            if p.direction == ViewDirections.US:
                self.us.append(p)
            if p.direction == ViewDirections.VA:
                self.va.append(p)

    def format_write(self):
        photo_str_list = ['Group={}'.format(self.group_name)]
        for photo in self.ds + self.us + self.va:
            photo_str_list.append('{:.3f},{:.3f},{:.5f},{},{}'.format(
                photo.easting or 0, photo.northing or 0, photo.bearing or 0,
                photo.filename or '', photo.direction or ''))
        return '\n'.join(photo_str_list)


class Photo(object):
    def __init__(self, easting, northing, bearing, filename, direction, remark):
        self.easting = float(easting)
        self.northing = float(northing)
        self.bearing = float(bearing)
        self.filename = filename
        self.direction = direction
        self.remark = remark


class CrossSectionHeaderGroup(object):
    group_name = 'Cross-section_Header'
    section_name_tag = 'Section_Name'
    section_description_tag = 'Section_Description'
    section_notes_tag = 'Section_Notes'
    complex_group_tag = 'Complex_Group'
    chainage_tag = 'Chainage'
    water_level_tag = 'Water_Level'
    section_type_tag = 'Section_Type'
    survey_date_tag = 'Survey_Date'
    survey_time_tag = 'Survey_Time'
    survey_method_tag = 'Survey_Method'

    tags = (section_name_tag, section_description_tag, section_notes_tag,
        complex_group_tag, chainage_tag, water_level_tag, section_type_tag,
        survey_date_tag, survey_time_tag, survey_method_tag)

    def __init__(self, section_name, section_description,
        section_notes, complex_group, chainage, water_level, section_type,
        survey_date, survey_time, survey_method):
        self.section_name = section_name
        self.reach, self.section_id = section_name.split('-')
        self.section_description = section_description
        self.section_notes = section_notes
        self.complex_group = complex_group
        self.chainage = float(chainage)
        self.chainage_id = '{0:05d}'.format(int(decimal.Decimal(chainage).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)))

        try:
            self.water_level = float(water_level)
        except ValueError:
            self.water_level = ''
        self.section_type = section_type

        if survey_date and survey_time:
            try:
                # Will parse EACSD date format 02Jun2017
                date = datetime.datetime.strptime(survey_date, '%d%b%Y')
            except ValueError:
                # Will try to parse everything else
                date = dateutil.parser.parse(survey_date, fuzzy=True).date()

            survey_datetime = datetime.datetime.combine(
                date,
                dateutil.parser.parse(survey_time, fuzzy=True).time())
        else:
            survey_datetime = None
        self.survey_datetime = survey_datetime
        self.survey_method = survey_method

        self.groups = []

    def format_write(self):
        if self.survey_datetime:
            survey_date = datetime.datetime.strftime(self.survey_datetime, '%d%b%Y')
            survey_time = self.survey_datetime.time()
        else:
            survey_date = ''
            survey_time = ''
        outstr = (
                'Group={}\n' +
                self.section_name_tag + '={}\n' +
                self.section_description_tag + '={}\n' +
                self.section_notes_tag + '={}\n' +
                self.complex_group_tag + '={}\n' +
                self.chainage_tag + '={}\n' +
                self.water_level_tag + '={}\n' +
                self.section_type_tag + '={}\n' +
                self.survey_date_tag + '={}\n' +
                self.survey_time_tag + '={}\n' +
                self.survey_method_tag + '={}').format(
            self.group_name, self.section_name, self.section_description,
            self.section_notes, self.complex_group, '{0:.3f}'.format(self.chainage),
            self.water_level, self.section_type, survey_date,
            survey_time, self.survey_method)

        return '\n*\n'.join([outstr] + [group.format_write() for group in self.groups])

    def add_group(self, group):
        self.groups.append(group)

    @property
    def upstream_photo(self):
        return self.photo_group.us

    def set_upstream_photo(self, filename, idx=0):
        self.photo_group.us[idx].filename = filename

    @property
    def downstream_photo(self):
        return self.photo_group.ds

    def set_downstream_photo(self, filename, idx=0):
        self.photo_group.ds[idx].filename = filename

    @property
    def across_photo(self):
        return self.photo_group.va

    def set_across_photo(self, filename, idx=0):
        self.photo_group.va[idx].filename = filename

    @property
    def photo_group(self):
        return self._photo_group

    @photo_group.setter
    def photo_group(self, group):
        self.add_group(group)
        if not isinstance(group, PhotoGroup):
            raise ValidationException('{} is not a PhotoGroup'.format(group))
        self._photo_group = group


class EACSD(object):
    group_name = 'File_Header'
    eacsd_v_tag = 'EACSD_V'
    watercourse_name_tag = 'Watercourse_Name'
    survey_title_tag = 'Survey_Title'
    revision_number_tag = 'Revision_Number'
    revision_comment_tag = 'Revision_Comment'
    date_of_file_preparation_tag = 'Date_of_File_Preparation'
    time_of_file_preparation_tag = 'Time_of_File_Preparation'
    file_produced_by_tag = 'File_Produced_by'
    surveyor_ref_tag = 'Surveyor_Ref'
    client_ref_tag = 'Client_Ref'
    nfcdd_watercourse_ref_tag = 'NFCDD_Watercourse_Ref'
    nfcdd_reach_ref_tag = 'NFCDD_Reach_Ref'
    nfcdd_sub_reach_ref_tag = 'NFCDD_Sub-reach_Ref'
    sos_reach_reference_tag = 'SoS_Reach_Reference'

    tags = (eacsd_v_tag, watercourse_name_tag, survey_title_tag,
        revision_number_tag, revision_comment_tag, date_of_file_preparation_tag,
        time_of_file_preparation_tag, file_produced_by_tag, surveyor_ref_tag,
        client_ref_tag, nfcdd_watercourse_ref_tag, nfcdd_reach_ref_tag,
        nfcdd_sub_reach_ref_tag, sos_reach_reference_tag)

    def __init__(self, eacsd_v, watercourse_name, survey_title, revision_number,
        revision_comment, date_of_file_preparation, time_of_file_preparation,
        file_produced_by, surveyor_ref, client_ref, nfcdd_watercourse_ref,
        nfcdd_reach_ref, nfcdd_sub_reach_ref, sos_reach_reference):

        self.eacsd_v = eacsd_v
        self.watercourse_name = watercourse_name
        self.survey_title = survey_title
        self.revision_number = revision_number
        self.revision_comment = revision_comment
        self.date_of_file_preparation = date_of_file_preparation
        self.time_of_file_preparation = time_of_file_preparation
        self.file_produced_by = file_produced_by
        self.surveyor_ref = surveyor_ref
        self.client_ref = client_ref
        self.nfcdd_watercourse_ref = nfcdd_watercourse_ref
        self.nfcdd_reach_ref = nfcdd_reach_ref
        self.nfcdd_sub_reach_ref = nfcdd_sub_reach_ref
        self.sos_reach_reference = sos_reach_reference

        self.groups = []
        self.cross_section_headers = OrderedDict()

    def add_cross_section(self, cross_section):
        if not isinstance(cross_section, CrossSectionHeaderGroup):
            raise ValidationException('{} is not a CrossSectionHeaderGroup'.format(cross_section))
        self.add_group(cross_section)
        self.cross_section_headers[cross_section.section_id] = cross_section

    def add_group(self, group):
        self.groups.append(group)

    def write(self):
        outstr = (
                'Group={}\n' +
                self.eacsd_v_tag + '={}\n' +
                self.watercourse_name_tag + '={}\n' +
                self.survey_title_tag + '={}\n' +
                self.revision_number_tag + '={}\n' +
                self.revision_comment_tag + '={}\n' +
                self.date_of_file_preparation_tag + '={}\n' +
                self.time_of_file_preparation_tag + '={}\n' +
                self.file_produced_by_tag + '={}\n' +
                self.surveyor_ref_tag + '={}\n' +
                self.client_ref_tag + '={}\n' +
                self.nfcdd_watercourse_ref_tag + '={}\n' +
                self.nfcdd_reach_ref_tag + '={}\n' +
                self.nfcdd_sub_reach_ref_tag + '={}\n' +
                self.sos_reach_reference_tag + '={}').format(
            self.group_name, self.eacsd_v, self.watercourse_name, self.survey_title,
            self.revision_number, self.revision_comment,
            self.date_of_file_preparation, self.time_of_file_preparation,
            self.file_produced_by, self.surveyor_ref, self.client_ref,
            self.nfcdd_watercourse_ref, self.nfcdd_reach_ref,
            self.nfcdd_sub_reach_ref, self.sos_reach_reference)

        return '\n*\n'.join([outstr] + [group.format_write() for group in self.groups]) + '\n*'