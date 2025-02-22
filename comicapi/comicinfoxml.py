"""A class to encapsulate ComicRack's ComicInfo.xml data"""

# Copyright 2012-2014 Anthony Beville

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xml.etree.ElementTree as ET
#from datetime import datetime
#from pprint import pprint
#import zipfile

from .genericmetadata import GenericMetadata
from .issuestring import IssueString
from . import utils


class ComicInfoXml:

    writer_synonyms = ['writer', 'plotter', 'scripter']
    penciller_synonyms = ['artist', 'penciller', 'penciler', 'breakdowns']
    inker_synonyms = ['inker', 'artist', 'finishes']
    colorist_synonyms = ['colorist', 'colourist', 'colorer', 'colourer']
    letterer_synonyms = ['letterer']
    cover_synonyms = ['cover', 'covers', 'coverartist', 'cover artist']
    editor_synonyms = ['editor']

    def getParseableCredits(self):
        parsable_credits = []
        parsable_credits.extend(self.writer_synonyms)
        parsable_credits.extend(self.penciller_synonyms)
        parsable_credits.extend(self.inker_synonyms)
        parsable_credits.extend(self.colorist_synonyms)
        parsable_credits.extend(self.letterer_synonyms)
        parsable_credits.extend(self.cover_synonyms)
        parsable_credits.extend(self.editor_synonyms)
        return parsable_credits

    def metadataFromString(self, string):

        tree = ET.ElementTree(ET.fromstring(string))
        return self.convertXMLToMetadata(tree)

    def stringFromMetadata(self, metadata, xml=None):

        header = '<?xml version="1.0"?>\n'

        tree = self.convertMetadataToXML(self, metadata, xml)
        tree_str = ET.tostring(tree.getroot()).decode()
        return header + tree_str

    def indent(self, elem, level=0):
        # for making the XML output readable
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def convertMetadataToXML(self, filename, metadata, xml=None):

        # shorthand for the metadata
        md = metadata

        if xml:
            root = ET.ElementTree(ET.fromstring(xml)).getroot()
        else:
            # build a tree structure
            root = ET.Element("ComicInfo")
            root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
            root.attrib['xmlns:xsd'] = "http://www.w3.org/2001/XMLSchema"
        # helper func

        def assign(cix_entry, md_entry):
            if md_entry is not None:
                print(cix_entry, md_entry)
                et_entry = root.find(cix_entry)
                if et_entry is not None:
                    et_entry.text = "{0}".format(md_entry)
                else:
                    ET.SubElement(root, cix_entry).text = "{0}".format(md_entry)

        assign('Title', md.title)
        assign('Series', md.series)
        assign('Number', md.issue)
        assign('Count', md.issueCount)
        assign('Volume', md.volume)
        assign('AlternateSeries', md.alternateSeries)
        assign('AlternateNumber', md.alternateNumber)
        assign('StoryArc', md.storyArc)
        assign('SeriesGroup', md.seriesGroup)
        assign('AlternateCount', md.alternateCount)
        assign('Summary', md.comments)
        assign('Notes', md.notes)
        assign('Year', md.year)
        assign('Month', md.month)
        assign('Day', md.day)

        # need to specially process the credits, since they are structured
        # differently than CIX
        credit_writer_list = list()
        credit_penciller_list = list()
        credit_inker_list = list()
        credit_colorist_list = list()
        credit_letterer_list = list()
        credit_cover_list = list()
        credit_editor_list = list()

        # first, loop thru credits, and build a list for each role that CIX
        # supports
        for credit in metadata.credits:

            if credit['role'].lower() in set(self.writer_synonyms):
                credit_writer_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.penciller_synonyms):
                credit_penciller_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.inker_synonyms):
                credit_inker_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.colorist_synonyms):
                credit_colorist_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.letterer_synonyms):
                credit_letterer_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.cover_synonyms):
                credit_cover_list.append(credit['person'].replace(",", ""))

            if credit['role'].lower() in set(self.editor_synonyms):
                credit_editor_list.append(credit['person'].replace(",", ""))

        # second, convert each list to string, and add to XML struct
        assign('Writer', utils.listToString(credit_writer_list))

        assign('Penciller', utils.listToString(credit_penciller_list))

        assign('Inker', utils.listToString(credit_inker_list))

        assign('Colorist', utils.listToString(credit_colorist_list))

        assign('Letterer', utils.listToString(credit_letterer_list))

        assign('CoverArtist', utils.listToString(credit_cover_list))

        assign('Editor', utils.listToString(credit_editor_list))

        assign('Publisher', md.publisher)
        assign('Imprint', md.imprint)
        assign('Genre', md.genre)
        assign('Web', md.webLink)
        assign('PageCount', md.pageCount)
        assign('LanguageISO', md.language)
        assign('Format', md.format)
        assign('AgeRating', md.maturityRating)
        if md.blackAndWhite is not None and md.blackAndWhite:
            assign('BlackAndWhite', "Yes")
        assign('Manga', md.manga)
        assign('Characters', md.characters)
        assign('Teams', md.teams)
        assign('Locations', md.locations)
        assign('ScanInformation', md.scanInfo)

        #  loop and add the page entries under pages node
        pages_node = root.find('Pages')
        if pages_node is not None:
            pages_node.clear()
        else:
            pages_node = ET.SubElement(root, 'Pages')

        for page_dict in md.pages:
            page_node = ET.SubElement(pages_node, 'Page')
            page_node.attrib = page_dict

        # self pretty-print
        self.indent(root)

        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(root)
        return tree

    def convertXMLToMetadata(self, tree):

        root = tree.getroot()

        if root.tag != 'ComicInfo':
            raise 1
            return None

        def get(name):
            tag = root.find(name)
            if tag is None:
                return None
            return tag.text

        md = GenericMetadata()

        md.series = utils.xlate(get('Series'))
        md.title = utils.xlate(get('Title'))
        md.issue = IssueString(utils.xlate(get('Number'))).asString()
        md.issueCount = utils.xlate(get('Count'), True)
        md.volume = utils.xlate(get('Volume'), True)
        md.alternateSeries = utils.xlate(get('AlternateSeries'))
        md.alternateNumber = IssueString(utils.xlate(get('AlternateNumber'))).asString()
        md.alternateCount = utils.xlate(get('AlternateCount'), True)
        md.comments = utils.xlate(get('Summary'))
        md.notes = utils.xlate(get('Notes'))
        md.year = utils.xlate(get('Year'), True)
        md.month = utils.xlate(get('Month'), True)
        md.day = utils.xlate(get('Day'), True)
        md.publisher = utils.xlate(get('Publisher'))
        md.imprint = utils.xlate(get('Imprint'))
        md.genre = utils.xlate(get('Genre'))
        md.webLink = utils.xlate(get('Web'))
        md.language = utils.xlate(get('LanguageISO'))
        md.format = utils.xlate(get('Format'))
        md.manga = utils.xlate(get('Manga'))
        md.characters = utils.xlate(get('Characters'))
        md.teams = utils.xlate(get('Teams'))
        md.locations = utils.xlate(get('Locations'))
        md.pageCount = utils.xlate(get('PageCount'), True)
        md.scanInfo = utils.xlate(get('ScanInformation'))
        md.storyArc = utils.xlate(get('StoryArc'))
        md.seriesGroup = utils.xlate(get('SeriesGroup'))
        md.maturityRating = utils.xlate(get('AgeRating'))

        tmp = utils.xlate(get('BlackAndWhite'))
        if tmp is not None and tmp.lower() in ["yes", "true", "1"]:
            md.blackAndWhite = True
        # Now extract the credit info
        for n in root:
            if (n.tag == 'Writer' or
                n.tag == 'Penciller' or
                n.tag == 'Inker' or
                n.tag == 'Colorist' or
                n.tag == 'Letterer' or
                n.tag == 'Editor'
                ):
                if n.text is not None:
                    for name in n.text.split(','):
                        md.addCredit(name.strip(), n.tag)

            if n.tag == 'CoverArtist':
                if n.text is not None:
                    for name in n.text.split(','):
                        md.addCredit(name.strip(), "Cover")

        # parse page data now
        pages_node = root.find("Pages")
        if pages_node is not None:
            for page in pages_node:
                md.pages.append(page.attrib)
                # print page.attrib

        md.isEmpty = False

        return md

    def writeToExternalFile(self, filename, metadata, xml=None):

        tree = self.convertMetadataToXML(self, metadata, xml)
        # ET.dump(tree)
        tree.write(filename, encoding='utf-8')

    def readFromExternalFile(self, filename):

        tree = ET.parse(filename)
        return self.convertXMLToMetadata(tree)
