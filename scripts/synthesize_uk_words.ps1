param([string]$QueueFile,[string]$VoiceName='Microsoft Hazel Desktop',[int]$Rate=-1,[string]$FfmpegPath='ffmpeg')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$taskSynth=New-Object System.Speech.Synthesis.SpeechSynthesizer
$taskSynth.SelectVoice($VoiceName)
if($taskSynth.Voice.Culture.Name -ne 'en-GB'){throw 'Selected voice must be en-GB'}
$taskSynth.Rate=$Rate
$taskItems=Get-Content -LiteralPath $QueueFile -Raw -Encoding UTF8 | ConvertFrom-Json
$taskDone=0;$taskFailed=0
try {
 foreach($taskItem in $taskItems){
  if((Test-Path -LiteralPath $taskItem.path) -and (Get-Item -LiteralPath $taskItem.path).Length -gt 1000){continue}
  $taskWav=$taskItem.path+'.wav'
  try {
   $taskSynth.SetOutputToWaveFile($taskWav)
   $taskSynth.Speak([string]$taskItem.text)
   $taskSynth.SetOutputToNull()
   & $FfmpegPath -hide_banner -loglevel error -y -i $taskWav -af 'silenceremove=start_periods=1:start_duration=0.01:start_threshold=-50dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_duration=0.01:start_threshold=-50dB:start_silence=0.10,areverse' -ar 24000 -ac 1 -codec:a libmp3lame -b:a 32k $taskItem.path
   if($LASTEXITCODE -ne 0){throw 'MP3 encoding failed'}
   Remove-Item -LiteralPath $taskWav
   $taskDone++
   if($taskDone%250 -eq 0){Write-Output "Generated $taskDone / $($taskItems.Count)"}
  } catch { $taskFailed++;Write-Output "FAILED $($taskItem.text): $_";if(Test-Path -LiteralPath $taskItem.path){Remove-Item -LiteralPath $taskItem.path} }
 }
} finally { $taskSynth.Dispose() }
Write-Output "Generated $taskDone; failed $taskFailed"
if($taskFailed -gt 0){exit 1}
