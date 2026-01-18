import dataclasses
import pathlib
import typing

Verbosity = int


@dataclasses.dataclass
class FileCounts:
    processed_templates: int
    saved_files: int

    def __add__(
        self,
        other: typing.Self,
    ) -> typing.Self:
        self.processed_templates += other.processed_templates
        self.saved_files += other.saved_files

        return self


TemplatePath = pathlib.Path
TemplatePaths = list[TemplatePath]

RenderedContent = str
ResultPath = pathlib.Path


JinjaOptionName = str
JinjaOptionValue = typing.Any

JinjaOptions = dict[JinjaOptionName, JinjaOptionValue]


NamespaceOptionName = str
NamespaceOptionValue = str

JinjaNamespace = dict[NamespaceOptionName, NamespaceOptionValue]
CustomNamespace = JinjaNamespace
TemplateNamespace = dict[str, JinjaNamespace]


JinjaExtensionName = str
JinjaExtensions = list[JinjaExtensionName]


CustomModuleName = str
CustomModules = list[CustomModuleName]
