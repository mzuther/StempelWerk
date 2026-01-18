import pathlib
import typing

Verbosity = int

FileCount = int
FileCounts = dict[str, FileCount]


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
