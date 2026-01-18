import pathlib
import typing

Verbosity = int


TemplatePath = pathlib.Path
TemplatePaths = list[TemplatePath]

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
