; Focus - Tam Kurulum Scripti (Tesseract + VC Redist + App)

[Setup]
AppName=Focus Exam Helper
AppVersion=1.3
DefaultDirName={localappdata}\Focus
DefaultGroupName=Focus
OutputBaseFilename=Focus_Kurulum_Full
Compression=lzma2
SolidCompression=yes
SetupIconFile=setup_files\icon.ico
PrivilegesRequired=admin

[Files]
Source: "setup_files\Focus.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "setup_files\tesseract-ocr-setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

Source: "setup_files\vcredist.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Focus"; Filename: "{app}\Focus.exe"; IconFilename: "{app}\Focus.exe"
Name: "{autodesktop}\Focus"; Filename: "{app}\Focus.exe"; IconFilename: "{app}\Focus.exe"

[Run]
Filename: "{tmp}\vcredist.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Gerekli sistem dosyaları (VC++) yükleniyor..."; Check: VCRedistGerekli

Filename: "{tmp}\tesseract-ocr-setup.exe"; Parameters: "/SILENT"; StatusMsg: "OCR Motoru (Tesseract) kuruluyor..."; Check: TesseractKuruluDegil

Filename: "{app}\Focus.exe"; Description: "Focus Uygulamasını Başlat"; Flags: nowait postinstall skipifsilent

[Code]
function TesseractKuruluDegil: Boolean;
begin
  if FileExists(ExpandConstant('{pf}\Tesseract-OCR\tesseract.exe')) then
    Result := False
  else
    Result := True;
end;

function VCRedistGerekli: Boolean;
begin
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') then
    Result := False
  else
    Result := True;
end;