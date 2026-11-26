import {parseSgf, serializeSgf} from "./sgf-core.js";
import {DEFAULT_AI_CONFIG, parseAiConfig, validateAiConfig} from "./ai-config.js";
const BLACK = 1, WHITE = 2;
const $ = (selector) => document.querySelector(selector);
const I18N = {
  'zh-Hant': {browserReady:'瀏覽器就緒',workbench:'你的圍棋工作室',title:'讓每一步，都值得推敲。',subtitle:'對弈、整理棋譜，或從新的變化開始研究。',newGame:'新棋局',openSgf:'開啟 SGF',currentGame:'目前棋局',unsaved:'未儲存',blackTurn:'黑棋下',whiteTurn:'白棋下',blackCaptured:'黑方提子',whiteCaptured:'白方提子',move:'手數',undo:'悔棋',redo:'重做',pass:'虛手',navigation:'棋譜導覽',gameTree:'棋譜樹',mainLine:'主線',fitTree:'適配',branchOnVariation:'只在分支處分岔',black:'黑',white:'白',variations:'變化',engine:'引擎',aiStudio:'AI 研究室',browserAiTitle:'瀏覽器 AI 引擎',browserAiBody:'確認 WebGPU 與可用記憶體。AI 引擎尚未連接，避免顯示虛構分析。',checkGpu:'檢查 WebGPU',visits:'搜尋次數',winrate:'勝率',scoreLead:'目差',engineNotBundled:'本次尚未整合可執行的 KataGo WebGPU/WASM 引擎，因此不提供假候選著。',review:'整盤覆盤',notAvailable:'尚未提供',details:'棋局資訊',gameInfo:'棋局資訊',edit:'編輯',blackPlayer:'黑方',whitePlayer:'白方',event:'賽事',result:'結果',comment:'目前節點註解',saveComment:'儲存註解',libraryLabel:'你的棋譜收藏',library:'棋譜庫',saveSgf:'匯出 SGF',localData:'棋局與偏好只儲存在此瀏覽器',installApp:'安裝網頁應用程式',settings:'設定',boardMaterial:'棋盤材質',stoneMaterial:'棋子材質',boardSize:'棋盤尺寸',fontSize:'字體大小',placementSound:'落子音效',preview:'試聽',motion:'動態背景',cancel:'取消',apply:'套用',editGameInfo:'編輯棋局資訊',komi:'貼目',librarySearch:'搜尋棋手、賽事、結果…',noGames:'尚無已儲存棋譜',saveFirst:'棋局已儲存到此瀏覽器',loaded:'已載入棋譜',saved:'棋譜已匯出',badSgf:'無法讀取這個 SGF 檔案',illegal:'這裡不能落子',gpuAvailable:'WebGPU 可用',gpuMissing:'WebGPU 不支援',gpuChecking:'檢查 GPU…',gpuAdapterMissing:'找不到 GPU 裝置',memoryEstimate:'瀏覽器回報約',memoryUnknown:'記憶體資訊不可用',enginePending:'引擎尚未整合',unsupported:'此棋步違反圍棋規則',gameOver:'雙方已連續虛手',confirmNew:'建立新棋局？未匯出的棋譜會先保留在本機收藏。',settingsApplied:'設定已套用',commentSaved:'註解已儲存',metadataSaved:'棋局資訊已更新',reviewNotReady:'瀏覽器 AI 引擎尚未整合',noBranch:'目前沒有後續棋步',moveLabel:'手',boardLabel:'棋盤',dark:'深色',light:'淺色',classicWood:'經典木紋',starfield:'星空',nightSky:'夜空',traditional:'傳統',starStones:'星空棋子',moonstone:'月岩',off:'關閉',subtle:'細緻',full:'完整',tagDefault:'本機收藏',exportTitle:'正在匯出棋譜',analyze:'分析局面',copySgf:'複製 SGF',aboutAI:'AI 推論尚未連接',materialPreview:'棋盤與棋子預覽'},
  'zh-Hans': {browserReady:'浏览器就绪',workbench:'你的围棋工作室',title:'让每一步，都值得推敲。',subtitle:'对弈、整理棋谱，或从新的变化开始研究。',newGame:'新棋局',openSgf:'打开 SGF',currentGame:'当前棋局',unsaved:'未保存',blackTurn:'黑棋下',whiteTurn:'白棋下',blackCaptured:'黑方提子',whiteCaptured:'白方提子',move:'手数',undo:'悔棋',redo:'重做',pass:'虚手',navigation:'棋谱导航',gameTree:'棋谱树',mainLine:'主线',fitTree:'适配',branchOnVariation:'仅在分支处分叉',black:'黑',white:'白',variations:'变化',engine:'引擎',aiStudio:'AI 研究室',browserAiTitle:'浏览器 AI 引擎',browserAiBody:'检查 WebGPU 与可用内存。AI 引擎尚未连接，因此不会显示虚构分析。',checkGpu:'检查 WebGPU',visits:'搜索次数',winrate:'胜率',scoreLead:'目差',engineNotBundled:'本次尚未集成可运行的 KataGo WebGPU/WASM 引擎，因此不提供虚假候选着。',review:'整盘复盘',notAvailable:'暂不可用',details:'棋局信息',gameInfo:'棋局信息',edit:'编辑',blackPlayer:'黑方',whitePlayer:'白方',event:'赛事',result:'结果',comment:'当前节点注释',saveComment:'保存注释',libraryLabel:'你的棋谱收藏',library:'棋谱库',saveSgf:'导出 SGF',localData:'棋局与偏好仅保存在此浏览器',installApp:'安装网页应用',settings:'设置',boardMaterial:'棋盘材质',stoneMaterial:'棋子材质',boardSize:'棋盘尺寸',fontSize:'字体大小',placementSound:'落子音效',preview:'试听',motion:'动态背景',cancel:'取消',apply:'应用',editGameInfo:'编辑棋局信息',komi:'贴目',librarySearch:'搜索棋手、赛事、结果…',noGames:'暂无已保存棋谱',saveFirst:'棋局已保存到此浏览器',loaded:'已载入棋谱',saved:'棋谱已导出',badSgf:'无法读取这个 SGF 文件',illegal:'这里不能落子',gpuAvailable:'WebGPU 可用',gpuMissing:'WebGPU 不支持',gpuChecking:'检查 GPU…',gpuAdapterMissing:'找不到 GPU 设备',memoryEstimate:'浏览器报告约',memoryUnknown:'内存信息不可用',enginePending:'引擎尚未集成',unsupported:'此棋步违反围棋规则',gameOver:'双方已连续虚手',confirmNew:'创建新棋局？未导出的棋谱会先保留在本地收藏。',settingsApplied:'设置已应用',commentSaved:'注释已保存',metadataSaved:'棋局信息已更新',reviewNotReady:'浏览器 AI 引擎尚未集成',noBranch:'当前没有后续棋步',moveLabel:'手',boardLabel:'棋盘',dark:'深色',light:'浅色',classicWood:'经典木纹',starfield:'星空',nightSky:'夜空',traditional:'传统',starStones:'星空棋子',moonstone:'月岩',off:'关闭',subtle:'细致',full:'完整',librarySearch:'搜索棋手、赛事、结果…',noGames:'暂无已保存棋谱',saveFirst:'棋局已保存到此浏览器',loaded:'已载入棋谱',saved:'棋谱已导出',badSgf:'无法读取这个 SGF 文件',gpuAvailable:'WebGPU 可用',gpuMissing:'WebGPU 不支持',gpuChecking:'检查 GPU…',enginePending:'引擎尚未集成',settingsApplied:'设置已应用',commentSaved:'注释已保存',metadataSaved:'棋局信息已更新',reviewNotReady:'浏览器 AI 引擎尚未集成',noBranch:'当前没有后续棋步',komi:'贴目',aboutAI:'AI 推论尚未连接'},
  en: {browserReady:'Browser ready',workbench:'YOUR GO WORKBENCH',title:'Make every move matter.',subtitle:'Play, organize game records, or study a new variation.',newGame:'New game',openSgf:'Open SGF',currentGame:'CURRENT GAME',unsaved:'Unsaved',blackTurn:'Black to play',whiteTurn:'White to play',blackCaptured:'Black captures',whiteCaptured:'White captures',move:'Move',undo:'Undo',redo:'Redo',pass:'Pass',navigation:'NAVIGATION',gameTree:'Game Tree',mainLine:'Main line',fitTree:'Fit',branchOnVariation:'Fork only at variations',black:'Black',white:'White',variations:'variations',engine:'ENGINE',aiStudio:'AI Studio',browserAiTitle:'Browser AI engine',browserAiBody:'Check WebGPU and available memory. The AI engine is not connected, so no fabricated analysis is shown.',checkGpu:'Check WebGPU',visits:'Visits',winrate:'Win rate',scoreLead:'Score lead',engineNotBundled:'A runnable KataGo WebGPU/WASM engine is not bundled yet, so candidate moves are not fabricated.',review:'Review full game',notAvailable:'Not available yet',details:'GAME DETAILS',gameInfo:'Game info',edit:'Edit',blackPlayer:'Black',whitePlayer:'White',event:'Event',result:'Result',comment:'Comment at this node',saveComment:'Save comment',libraryLabel:'YOUR COLLECTION',library:'Game library',saveSgf:'Export SGF',localData:'Games and preferences stay in this browser',installApp:'Install web app',settings:'Settings',boardMaterial:'Board material',stoneMaterial:'Stone material',boardSize:'Board size',fontSize:'Font size',placementSound:'Placement sound',preview:'Preview',motion:'Ambient motion',cancel:'Cancel',apply:'Apply',editGameInfo:'Edit game info',komi:'Komi',librarySearch:'Search player, event, result…',noGames:'No saved games yet',saveFirst:'Game saved in this browser',loaded:'Game loaded',saved:'SGF exported',badSgf:'Could not read this SGF file',illegal:'That move is not legal',gpuAvailable:'WebGPU available',gpuMissing:'WebGPU unsupported',gpuChecking:'Checking GPU…',gpuAdapterMissing:'No GPU adapter found',memoryEstimate:'Browser reports about',memoryUnknown:'Memory information unavailable',enginePending:'Engine not integrated',unsupported:'This move violates Go rules',gameOver:'Both players passed consecutively',confirmNew:'Start a new game? The current game will first be kept in your local library.',settingsApplied:'Settings applied',commentSaved:'Comment saved',metadataSaved:'Game info updated',reviewNotReady:'Browser AI engine is not integrated yet',noBranch:'No continuation here',moveLabel:'Move',boardLabel:'Board',dark:'Dark',light:'Light',classicWood:'Classic wood',starfield:'Starfield',nightSky:'Night sky',traditional:'Traditional',starStones:'Star stones',moonstone:'Moonstone',off:'Off',subtle:'Subtle',full:'Full',aboutAI:'AI inference is not connected'},
  ja: {browserReady:'ブラウザー準備完了',workbench:'囲碁ワークベンチ',title:'一手一手を、深く味わう。',subtitle:'対局、棋譜の整理、新しい変化の研究。',newGame:'新しい対局',openSgf:'SGFを開く',currentGame:'現在の対局',unsaved:'未保存',blackTurn:'黒番',whiteTurn:'白番',blackCaptured:'黒のアゲハマ',whiteCaptured:'白のアゲハマ',move:'手数',undo:'戻す',redo:'やり直す',pass:'パス',navigation:'棋譜ナビゲーション',gameTree:'棋譜ツリー',mainLine:'本線',fitTree:'全体表示',branchOnVariation:'変化点のみ分岐',black:'黒',white:'白',variations:'変化',engine:'エンジン',aiStudio:'AIスタジオ',browserAiTitle:'ブラウザーAIエンジン',browserAiBody:'WebGPUとメモリーを確認します。AIエンジン未接続のため、架空の解析は表示しません。',checkGpu:'WebGPUを確認',visits:'探索数',winrate:'勝率',scoreLead:'目差',engineNotBundled:'KataGo WebGPU/WASMエンジンは未同梱です。候補手を捏造して表示しません。',review:'全局検討',notAvailable:'未対応',details:'対局情報',gameInfo:'対局情報',edit:'編集',blackPlayer:'黒番',whitePlayer:'白番',event:'大会',result:'結果',comment:'この局面のコメント',saveComment:'コメントを保存',libraryLabel:'棋譜コレクション',library:'棋譜ライブラリー',saveSgf:'SGFを書き出す',localData:'棋譜と設定はこのブラウザーに保存',installApp:'ウェブアプリをインストール',settings:'設定',boardMaterial:'盤の素材',stoneMaterial:'碁石の素材',boardSize:'盤サイズ',fontSize:'文字サイズ',placementSound:'着手音',preview:'試聴',motion:'背景アニメーション',cancel:'キャンセル',apply:'適用',editGameInfo:'対局情報を編集',komi:'コミ',librarySearch:'棋士・大会・結果を検索…',noGames:'保存済み棋譜はありません',saveFirst:'このブラウザーに保存しました',loaded:'棋譜を読み込みました',saved:'SGFを書き出しました',badSgf:'SGFを読み込めません',illegal:'そこには着手できません',gpuAvailable:'WebGPU利用可能',gpuMissing:'WebGPU非対応',gpuChecking:'GPUを確認中…',gpuAdapterMissing:'GPUアダプターがありません',enginePending:'エンジン未統合',settingsApplied:'設定を適用しました',commentSaved:'コメントを保存しました',metadataSaved:'対局情報を更新しました',reviewNotReady:'ブラウザーAIエンジンは未統合です',noBranch:'続きの手はありません',komi:'コミ',aboutAI:'AI推論未接続'},
  ko: {browserReady:'브라우저 준비 완료',workbench:'바둑 워크벤치',title:'한 수 한 수, 깊이 생각하다.',subtitle:'대국하고 기보를 정리하며 새로운 변화를 연구하세요.',newGame:'새 대국',openSgf:'SGF 열기',currentGame:'현재 대국',unsaved:'저장되지 않음',blackTurn:'흑 차례',whiteTurn:'백 차례',blackCaptured:'흑 포획',whiteCaptured:'백 포획',move:'수',undo:'무르기',redo:'다시 실행',pass:'패스',navigation:'기보 탐색',gameTree:'기보 트리',mainLine:'주요 진행',fitTree:'맞춤',branchOnVariation:'변화점에서만 분기',black:'흑',white:'백',variations:'변화',engine:'엔진',aiStudio:'AI 스튜디오',browserAiTitle:'브라우저 AI 엔진',browserAiBody:'WebGPU와 메모리를 확인합니다. AI 엔진이 연결되지 않아 가짜 분석은 표시하지 않습니다.',checkGpu:'WebGPU 확인',visits:'탐색 횟수',winrate:'승률',scoreLead:'집 차이',engineNotBundled:'실행 가능한 KataGo WebGPU/WASM 엔진이 아직 포함되지 않아 후보 수를 표시하지 않습니다.',review:'전체 복기',notAvailable:'아직 사용할 수 없음',details:'대국 정보',gameInfo:'대국 정보',edit:'편집',blackPlayer:'흑',whitePlayer:'백',event:'대회',result:'결과',comment:'현재 노드 주석',saveComment:'주석 저장',libraryLabel:'내 기보 컬렉션',library:'기보 라이브러리',saveSgf:'SGF 내보내기',localData:'대국과 설정은 이 브라우저에 저장됩니다',installApp:'웹 앱 설치',settings:'설정',boardMaterial:'바둑판 재질',stoneMaterial:'바둑돌 재질',boardSize:'판 크기',fontSize:'글꼴 크기',placementSound:'착수 효과음',preview:'미리 듣기',motion:'배경 움직임',cancel:'취소',apply:'적용',editGameInfo:'대국 정보 편집',komi:'덤',librarySearch:'기사·대회·결과 검색…',noGames:'저장된 기보가 없습니다',saveFirst:'이 브라우저에 저장했습니다',loaded:'기보를 불러왔습니다',saved:'SGF를 내보냈습니다',badSgf:'SGF를 읽을 수 없습니다',illegal:'그곳에는 둘 수 없습니다',gpuAvailable:'WebGPU 사용 가능',gpuMissing:'WebGPU 미지원',gpuChecking:'GPU 확인 중…',gpuAdapterMissing:'GPU 어댑터 없음',enginePending:'엔진 미통합',settingsApplied:'설정을 적용했습니다',commentSaved:'주석을 저장했습니다',metadataSaved:'대국 정보를 갱신했습니다',reviewNotReady:'브라우저 AI 엔진이 아직 통합되지 않았습니다',noBranch:'다음 수가 없습니다',komi:'덤',aboutAI:'AI 분석 미연결'}
};
Object.assign(I18N['zh-Hant'],{theme:'介面主題',classicWood:'經典木紋',starfield:'星空',nightSky:'夜空',traditional:'傳統',starStones:'星空棋子',moonstone:'月岩',off:'關閉',subtle:'細緻',full:'完整'});
Object.assign(I18N['zh-Hans'],{theme:'界面主题',classicWood:'经典木纹',starfield:'星空',nightSky:'夜空',traditional:'传统',starStones:'星空棋子',moonstone:'月岩',off:'关闭',subtle:'细致',full:'完整'});
Object.assign(I18N.en,{theme:'Interface theme',classicWood:'Classic wood',starfield:'Starfield',nightSky:'Night sky',traditional:'Traditional',starStones:'Star stones',moonstone:'Moonstone',off:'Off',subtle:'Subtle',full:'Full'});
Object.assign(I18N.ja,{theme:'画面テーマ',classicWood:'クラシック木目',starfield:'星空',nightSky:'夜空',traditional:'伝統',starStones:'星空の碁石',moonstone:'月岩',off:'オフ',subtle:'控えめ',full:'完全'});
Object.assign(I18N.ko,{theme:'화면 테마',classicWood:'클래식 나무결',starfield:'별무리',nightSky:'밤하늘',traditional:'전통',starStones:'별무리 바둑돌',moonstone:'월석',off:'끄기',subtle:'은은하게',full:'전체'});
const AI_SETUP_I18N={
 'zh-Hant':{setupModel:'AI 模型',setupProfile:'AI 設定文件',setupReady:'已設定',setupMissing:'尚未設定',gpuReadySetupPrompt:'WebGPU 可用。請先匯入 AI 模型，並建立或匯入 AI 設定文件，才能開始分析。',gpuReadyModelPrompt:'WebGPU 可用。請先匯入 AI 模型，再建立或匯入 AI 設定文件。',gpuReadyComplete:'WebGPU、模型與 AI 設定文件都已就緒。',gpuBeforeSetup:'請先確認 WebGPU，並在「設定 AI」中匯入模型與 AI 設定文件。',profileTitle:'AI 設定文件',profileHelp:'匯入 NightyGo Web JSON 設定文件，或依上方搜尋預算產生一份。文件只保存在此瀏覽器。',createProfile:'建立並下載設定文件',importProfile:'匯入 JSON 文件',exportProfile:'匯出設定文件',profileMissing:'尚未設定 AI 文件',profileReady:'AI 設定文件已就緒',profileImported:'AI 設定文件已匯入',searchTimeLimit:'單次搜尋時間',timeShort:'5 秒',timeStandard:'15 秒',timeLong:'30 秒',searchBudget:'搜尋預算',fastBudget:'32 次 · 快速',balancedBudget:'128 次 · 平衡',deepBudget:'512 次 · 深度',configureAi:'設定 AI',needModel:'請先匯入 AI 模型。',needProfile:'請先建立或匯入 AI 設定文件。',modelNotFound:'找不到本機模型。'},
 'zh-Hans':{setupModel:'AI 模型',setupProfile:'AI 设置文件',setupReady:'已配置',setupMissing:'尚未配置',gpuReadySetupPrompt:'WebGPU 可用。请先导入 AI 模型，并创建或导入 AI 设置文件，才能开始分析。',gpuReadyModelPrompt:'WebGPU 可用。请先导入 AI 模型，再创建或导入 AI 设置文件。',gpuReadyComplete:'WebGPU、模型和 AI 设置文件都已就绪。',gpuBeforeSetup:'请先确认 WebGPU，并在“设置 AI”中导入模型与 AI 设置文件。',profileTitle:'AI 设置文件',profileHelp:'导入 NightyGo Web JSON 设置文件，或按上方搜索预算生成一份。文件仅保存在此浏览器。',createProfile:'创建并下载设置文件',importProfile:'导入 JSON 文件',exportProfile:'导出设置文件',profileMissing:'尚未配置 AI 文件',profileReady:'AI 设置文件已就绪',profileImported:'AI 设置文件已导入',searchTimeLimit:'单次搜索时间',timeShort:'5 秒',timeStandard:'15 秒',timeLong:'30 秒',searchBudget:'搜索预算',fastBudget:'32 次 · 快速',balancedBudget:'128 次 · 均衡',deepBudget:'512 次 · 深度',configureAi:'设置 AI',needModel:'请先导入 AI 模型。',needProfile:'请先创建或导入 AI 设置文件。',modelNotFound:'找不到本地模型。'},
 en:{setupModel:'AI model',setupProfile:'AI profile file',setupReady:'Ready',setupMissing:'Not set up',gpuReadySetupPrompt:'WebGPU is available. Import an AI model and create or import an AI profile file before analysis.',gpuReadyModelPrompt:'WebGPU is available. Import an AI model, then create or import an AI profile file.',gpuReadyComplete:'WebGPU, model, and AI profile are ready.',gpuBeforeSetup:'Check WebGPU, then use “Configure AI” to import a model and AI profile file.',profileTitle:'AI profile file',profileHelp:'Import a NightyGo Web JSON profile or create one from the search options above. It stays in this browser.',createProfile:'Create and download profile',importProfile:'Import JSON profile',exportProfile:'Export profile',profileMissing:'AI profile not set up',profileReady:'AI profile is ready',profileImported:'AI profile imported',searchTimeLimit:'Search time limit',timeShort:'5 seconds',timeStandard:'15 seconds',timeLong:'30 seconds',searchBudget:'Search budget',fastBudget:'32 visits · Fast',balancedBudget:'128 visits · Balanced',deepBudget:'512 visits · Deep',configureAi:'Configure AI',needModel:'Import an AI model first.',needProfile:'Create or import an AI profile file first.',modelNotFound:'Local model not found.'},
 ja:{setupModel:'AIモデル',setupProfile:'AI設定ファイル',setupReady:'準備完了',setupMissing:'未設定',gpuReadySetupPrompt:'WebGPUを利用できます。解析を始める前にAIモデルを読み込み、AI設定ファイルを作成または読み込んでください。',gpuReadyModelPrompt:'WebGPUを利用できます。AIモデルを読み込み、AI設定ファイルを作成または読み込んでください。',gpuReadyComplete:'WebGPU、モデル、AI設定ファイルの準備ができました。',gpuBeforeSetup:'WebGPUを確認し、「AIを設定」からモデルと設定ファイルを読み込んでください。',profileTitle:'AI設定ファイル',profileHelp:'NightyGo WebのJSON設定ファイルを読み込むか、上の検索設定から作成できます。このブラウザー内に保存されます。',createProfile:'設定ファイルを作成・保存',importProfile:'JSONを読み込む',exportProfile:'設定を保存',profileMissing:'AI設定ファイル未設定',profileReady:'AI設定ファイル準備完了',profileImported:'AI設定ファイルを読み込みました',searchTimeLimit:'1回の探索時間',timeShort:'5秒',timeStandard:'15秒',timeLong:'30秒',searchBudget:'探索予算',fastBudget:'32回 · 高速',balancedBudget:'128回 · 標準',deepBudget:'512回 · 深い',configureAi:'AIを設定',needModel:'先にAIモデルを読み込んでください。',needProfile:'先にAI設定ファイルを作成または読み込んでください。',modelNotFound:'ローカルモデルが見つかりません。'},
 ko:{setupModel:'AI 모델',setupProfile:'AI 설정 파일',setupReady:'준비 완료',setupMissing:'미설정',gpuReadySetupPrompt:'WebGPU를 사용할 수 있습니다. 분석 전에 AI 모델을 가져오고 AI 설정 파일을 만들거나 가져오세요.',gpuReadyModelPrompt:'WebGPU를 사용할 수 있습니다. AI 모델을 가져온 뒤 AI 설정 파일을 만들거나 가져오세요.',gpuReadyComplete:'WebGPU, 모델, AI 설정 파일이 준비되었습니다.',gpuBeforeSetup:'WebGPU를 확인한 뒤 “AI 설정”에서 모델과 설정 파일을 가져오세요.',profileTitle:'AI 설정 파일',profileHelp:'NightyGo Web JSON 설정 파일을 가져오거나 위 검색 옵션으로 만들 수 있습니다. 이 브라우저에 저장됩니다.',createProfile:'설정 파일 만들고 다운로드',importProfile:'JSON 파일 가져오기',exportProfile:'설정 파일 내보내기',profileMissing:'AI 설정 파일 미설정',profileReady:'AI 설정 파일 준비 완료',profileImported:'AI 설정 파일을 가져왔습니다',searchTimeLimit:'한 번의 탐색 시간',timeShort:'5초',timeStandard:'15초',timeLong:'30초',searchBudget:'탐색 예산',fastBudget:'32회 · 빠름',balancedBudget:'128회 · 균형',deepBudget:'512회 · 깊게',configureAi:'AI 설정',needModel:'먼저 AI 모델을 가져오세요.',needProfile:'먼저 AI 설정 파일을 만들거나 가져오세요.',modelNotFound:'로컬 모델을 찾을 수 없습니다.'}
};
for(const [locale,values] of Object.entries(AI_SETUP_I18N))Object.assign(I18N[locale],values);
const MAIL_I18N={
 'zh-Hant':{sendMail:'寄送郵件',mailIntro:'輸入收件者 Email，將在你的郵件 App 開啟草稿，棋譜會放在郵件內容中。',emailAddress:'收件者 Email',mailStorageNote:'此 Email 只儲存在這台裝置的 NightyGo 網站資料中；清除網站資料或快取前會一直保留，方便下次使用。',openMail:'開啟郵件草稿',mailTooLarge:'棋譜太長，無法放入郵件草稿。請改用「匯出 SGF」後附加檔案。',mailSubject:'NightyGo 圍棋棋譜',mailBody:'你好，這是我分享的圍棋棋譜。SGF 內容如下：'},
 'zh-Hans':{sendMail:'发送邮件',mailIntro:'输入收件人 Email，将在你的邮件 App 中打开草稿，棋谱会放在邮件正文中。',emailAddress:'收件人 Email',mailStorageNote:'此 Email 仅保存在这台设备的 NightyGo 网站数据中；清除网站数据或缓存前会一直保留，方便下次使用。',openMail:'打开邮件草稿',mailTooLarge:'棋谱太长，无法放入邮件草稿。请改用“导出 SGF”后添加附件。',mailSubject:'NightyGo 围棋棋谱',mailBody:'你好，这是我分享的围棋棋谱。SGF 内容如下：'},
 en:{sendMail:'Send Mail',mailIntro:'Enter a recipient email. Your mail app will open a draft with the game record in the message body.',emailAddress:'Recipient email',mailStorageNote:'This email is stored only in NightyGo site data on this device. It stays available until you clear this site’s data or cache.',openMail:'Open mail draft',mailTooLarge:'This game is too large to fit in a mail draft. Export the SGF and attach the file instead.',mailSubject:'NightyGo Go game record',mailBody:'Hello, here is the Go game record I am sharing. SGF follows:'},
 ja:{sendMail:'メールで送る',mailIntro:'宛先のメールアドレスを入力すると、棋譜を本文に含むメールの下書きをメールアプリで開きます。',emailAddress:'宛先メールアドレス',mailStorageNote:'メールアドレスはこの端末のNightyGoサイトデータにのみ保存され、サイトデータまたはキャッシュを消去するまで保持されます。',openMail:'メールの下書きを開く',mailTooLarge:'棋譜が長すぎてメールの下書きに入りません。「SGFを書き出す」を使ってファイルを添付してください。',mailSubject:'NightyGo 囲碁棋譜',mailBody:'こんにちは。共有する囲碁棋譜です。SGF：'},
 ko:{sendMail:'메일 보내기',mailIntro:'받는 사람 이메일을 입력하면 기보가 본문에 포함된 초안을 메일 앱에서 엽니다.',emailAddress:'받는 사람 이메일',mailStorageNote:'이 이메일은 이 기기의 NightyGo 사이트 데이터에만 저장되며 사이트 데이터나 캐시를 지울 때까지 유지됩니다.',openMail:'메일 초안 열기',mailTooLarge:'기보가 너무 길어 메일 초안에 넣을 수 없습니다. SGF 내보내기를 사용해 파일을 첨부하세요.',mailSubject:'NightyGo 바둑 기보',mailBody:'안녕하세요. 공유할 바둑 기보입니다. SGF:'}
};
for(const [locale,values] of Object.entries(MAIL_I18N))Object.assign(I18N[locale],values);
Object.assign(I18N['zh-Hans'],{browserReady:'浏览器就绪',currentGame:'当前棋局',unsaved:'未保存',blackCaptured:'黑方提子',move:'手数',whiteCaptured:'白方提子',navigation:'棋谱导航',gameTree:'棋谱树',mainLine:'主线',fitTree:'适配',branchOnVariation:'只在分支处分叉',black:'黑',white:'白',variations:'变化',engine:'引擎',aiStudio:'AI 研究室',browserAiTitle:'浏览器 AI 引擎',browserAiBody:'检查 WebGPU 与可用内存。AI 引擎尚未连接，因此不会显示虚构分析。',checkGpu:'检查 WebGPU',visits:'搜索次数',winrate:'胜率',scoreLead:'目差',engineNotBundled:'本次尚未集成可运行的 KataGo WebGPU/WASM 引擎，因此不提供虚假候选着。',review:'整盘复盘',notAvailable:'暂不可用',details:'棋局信息',gameInfo:'棋局信息',edit:'编辑',blackPlayer:'黑方',whitePlayer:'白方',event:'赛事',result:'结果',comment:'当前节点注释',saveComment:'保存注释',libraryLabel:'你的棋谱收藏',library:'棋谱库',saveSgf:'导出 SGF',localData:'棋局与偏好仅保存在此浏览器',installApp:'安装网页应用',settings:'设置',theme:'界面主题',dark:'深色',light:'浅色',boardMaterial:'棋盘材质',stoneMaterial:'棋子材质',boardSize:'棋盘尺寸',fontSize:'字体大小',placementSound:'落子音效',preview:'试听',motion:'动态背景',cancel:'取消',apply:'应用',editGameInfo:'编辑棋局信息',komi:'贴目'});
Object.assign(I18N.ja,{browserReady:'ブラウザー準備完了',workbench:'囲碁ワークベンチ',subtitle:'対局、棋譜の整理、新しい変化の研究。',currentGame:'現在の対局',unsaved:'未保存',blackTurn:'黒番',whiteTurn:'白番',blackCaptured:'黒のアゲハマ',whiteCaptured:'白のアゲハマ',move:'手数',undo:'戻す',redo:'やり直す',pass:'パス',navigation:'棋譜ナビゲーション',gameTree:'棋譜ツリー',mainLine:'本線',fitTree:'全体表示',branchOnVariation:'変化点のみ分岐',black:'黒',white:'白',variations:'変化',engine:'エンジン',aiStudio:'AIスタジオ',browserAiTitle:'ブラウザーAIエンジン',browserAiBody:'WebGPUとメモリーを確認します。AIエンジン未接続のため、架空の解析は表示しません。',checkGpu:'WebGPUを確認',visits:'探索数',winrate:'勝率',scoreLead:'目差',engineNotBundled:'KataGo WebGPU/WASMエンジンは未同梱です。候補手を捏造して表示しません。',review:'全局検討',notAvailable:'未対応',details:'対局情報',gameInfo:'対局情報',edit:'編集',blackPlayer:'黒番',whitePlayer:'白番',event:'大会',result:'結果',comment:'この局面のコメント',saveComment:'コメントを保存',libraryLabel:'棋譜コレクション',library:'棋譜ライブラリー',saveSgf:'SGFを書き出す',localData:'棋譜と設定はこのブラウザーに保存',installApp:'ウェブアプリをインストール',settings:'設定',theme:'画面テーマ',dark:'ダーク',light:'ライト',boardMaterial:'盤の素材',stoneMaterial:'碁石の素材',boardSize:'盤サイズ',fontSize:'文字サイズ',placementSound:'着手音',preview:'試聴',motion:'背景アニメーション',cancel:'キャンセル',apply:'適用',editGameInfo:'対局情報を編集',komi:'コミ'});
Object.assign(I18N.ko,{browserReady:'브라우저 준비 완료',workbench:'바둑 워크벤치',subtitle:'대국하고 기보를 정리하며 새로운 변화를 연구하세요.',currentGame:'현재 대국',unsaved:'저장되지 않음',blackTurn:'흑 차례',whiteTurn:'백 차례',blackCaptured:'흑 포획',whiteCaptured:'백 포획',move:'수',undo:'무르기',redo:'다시 실행',pass:'패스',navigation:'기보 탐색',gameTree:'기보 트리',mainLine:'주요 진행',fitTree:'맞춤',branchOnVariation:'변화점에서만 분기',black:'흑',white:'백',variations:'변화',engine:'엔진',aiStudio:'AI 스튜디오',browserAiTitle:'브라우저 AI 엔진',browserAiBody:'WebGPU와 메모리를 확인합니다. AI 엔진이 연결되지 않아 가짜 분석은 표시하지 않습니다.',checkGpu:'WebGPU 확인',visits:'탐색 횟수',winrate:'승률',scoreLead:'집 차이',engineNotBundled:'실행 가능한 KataGo WebGPU/WASM 엔진이 아직 포함되지 않아 후보 수를 표시하지 않습니다.',review:'전체 복기',notAvailable:'아직 사용할 수 없음',details:'대국 정보',gameInfo:'대국 정보',edit:'편집',blackPlayer:'흑',whitePlayer:'백',event:'대회',result:'결과',comment:'현재 노드 주석',saveComment:'주석 저장',libraryLabel:'내 기보 컬렉션',library:'기보 라이브러리',saveSgf:'SGF 내보내기',localData:'대국과 설정은 이 브라우저에 저장됩니다',installApp:'웹 앱 설치',settings:'설정',theme:'화면 테마',dark:'다크',light:'라이트',boardMaterial:'바둑판 재질',stoneMaterial:'바둑돌 재질',boardSize:'판 크기',fontSize:'글꼴 크기',placementSound:'착수 효과음',preview:'미리 듣기',motion:'배경 움직임',cancel:'취소',apply:'적용',editGameInfo:'대국 정보 편집',komi:'덤'});
Object.assign(I18N['zh-Hant'],{sound1:'木板落子 1',sound2:'木板落子 2',sound3:'木板落子 3',sound4:'木板落子 4',sound5:'木板落子 5',versus:' 對 ',browserTitle:'未命名棋局'});
Object.assign(I18N['zh-Hans'],{sound1:'木板落子 1',sound2:'木板落子 2',sound3:'木板落子 3',sound4:'木板落子 4',sound5:'木板落子 5',versus:' 对 ',browserTitle:'未命名棋局'});
Object.assign(I18N.en,{sound1:'Wooden board · 1',sound2:'Wooden board · 2',sound3:'Wooden board · 3',sound4:'Thin board · 1',sound5:'Thin board · 2',versus:' vs ',browserTitle:'Untitled game'});
Object.assign(I18N.ja,{sound1:'木の碁盤 · 1',sound2:'木の碁盤 · 2',sound3:'木の碁盤 · 3',sound4:'薄い碁盤 · 1',sound5:'薄い碁盤 · 2',versus:' 対 ',browserTitle:'無題の対局'});
Object.assign(I18N.ko,{sound1:'나무 바둑판 · 1',sound2:'나무 바둑판 · 2',sound3:'나무 바둑판 · 3',sound4:'얇은 바둑판 · 1',sound5:'얇은 바둑판 · 2',versus:' 대 ',browserTitle:'제목 없는 대국'});
Object.assign(I18N['zh-Hant'],{markup:'棋盤標記',noMarkup:'無',triangle:'三角形',square:'方形',circle:'圓形',cross:'叉號',label:'標籤'});
Object.assign(I18N['zh-Hans'],{markup:'棋盘标记',noMarkup:'无',triangle:'三角形',square:'方形',circle:'圆形',cross:'叉号',label:'标签'});
Object.assign(I18N.en,{markup:'Board marks',noMarkup:'None',triangle:'Triangle',square:'Square',circle:'Circle',cross:'Cross',label:'Label'});
Object.assign(I18N.ja,{markup:'盤面マーク',noMarkup:'なし',triangle:'三角',square:'四角',circle:'丸',cross:'バツ',label:'ラベル'});
Object.assign(I18N.ko,{markup:'바둑판 표시',noMarkup:'없음',triangle:'삼각형',square:'사각형',circle:'원',cross:'십자',label:'라벨'});
Object.assign(I18N['zh-Hant'],{browserAiBody:'AI 在本機瀏覽器執行。請到模型管理匯入 KataGo 網路檔。',modelConfig:'AI Model Config',modelIntro:'模型儲存在此瀏覽器，不會上傳。官方模型需先下載再匯入 .bin.gz。',modelFile:'匯入 .bin.gz',localModel:'本機模型',searchBudget:'搜尋預算',noModel:'尚未匯入模型',downloadLight:'下載輕量官方模型 ↗',downloadBalanced:'下載平衡官方模型 ↗',downloadStrong:'下載最新高強度模型 ↗',chooseGame:'選擇棋局',collectionInfo:'此 SGF 包含多局棋譜。匯出時會保留整個集合。',openGame:'開啟棋局',scoreGame:'計分',handicap:'讓子（0–9）'});
Object.assign(I18N['zh-Hans'],{browserAiBody:'AI 在本地浏览器运行。请到模型管理导入 KataGo 网络文件。',modelConfig:'AI Model Config',modelIntro:'模型存储在此浏览器，不会上传。官方模型需先下载再导入 .bin.gz。',modelFile:'导入 .bin.gz',localModel:'本地模型',searchBudget:'搜索预算',noModel:'尚未导入模型',downloadLight:'下载轻量官方模型 ↗',downloadBalanced:'下载平衡官方模型 ↗',downloadStrong:'下载最新高强度模型 ↗',chooseGame:'选择棋局',collectionInfo:'此 SGF 包含多局棋谱。导出时会保留整个集合。',openGame:'打开棋局',scoreGame:'计分',handicap:'让子（0–9）'});
Object.assign(I18N.en,{browserAiBody:'AI runs locally in this browser. Import a KataGo network file in Model Manager.',modelConfig:'AI Model Config',modelIntro:'Models stay in this browser and are never uploaded. Download an official model, then import its .bin.gz file.',modelFile:'Import .bin.gz',localModel:'Local model',searchBudget:'Search budget',noModel:'No model imported',downloadLight:'Download light official model ↗',downloadBalanced:'Download balanced official model ↗',downloadStrong:'Download latest strong model ↗',chooseGame:'Choose a game',collectionInfo:'This SGF contains multiple games. Export preserves the complete collection.',openGame:'Open game',scoreGame:'Score',handicap:'Handicap (0–9)'});
Object.assign(I18N.ja,{browserAiBody:'AIはこのブラウザー内で実行します。モデル管理からKataGoネットワークを読み込んでください。',modelConfig:'AI Model Config',modelIntro:'モデルはこのブラウザー内に保存され、アップロードされません。公式モデルをダウンロードして.bin.gzを読み込んでください。',modelFile:'.bin.gzを読み込む',localModel:'ローカルモデル',searchBudget:'探索回数',noModel:'モデル未読込',downloadLight:'軽量公式モデルをダウンロード ↗',downloadBalanced:'標準公式モデルをダウンロード ↗',downloadStrong:'最新高性能モデルをダウンロード ↗',chooseGame:'棋譜を選択',collectionInfo:'複数の棋譜が含まれます。書き出しでは全棋譜を保持します。',openGame:'棋譜を開く',scoreGame:'計算',handicap:'置き石（0～9）'});
Object.assign(I18N.ko,{browserAiBody:'AI는 이 브라우저에서 실행됩니다. 모델 관리에서 KataGo 네트워크 파일을 가져오세요.',modelConfig:'AI Model Config',modelIntro:'모델은 이 브라우저에만 저장되며 업로드되지 않습니다. 공식 모델을 다운로드한 뒤 .bin.gz 파일을 가져오세요.',modelFile:'.bin.gz 가져오기',localModel:'로컬 모델',searchBudget:'탐색 횟수',noModel:'가져온 모델 없음',downloadLight:'경량 공식 모델 다운로드 ↗',downloadBalanced:'균형 공식 모델 다운로드 ↗',downloadStrong:'최신 강력 모델 다운로드 ↗',chooseGame:'기보 선택',collectionInfo:'여러 기보가 들어 있습니다. 내보내면 전체 컬렉션을 보존합니다.',openGame:'기보 열기',scoreGame:'계산',handicap:'접바둑 (0–9)'});
for(const [locale,values] of Object.entries({'zh-Hant':{lineTool:'線段',arrowTool:'箭頭',fastBudget:'32 visits · 快速',balancedBudget:'128 visits · 平衡',deepBudget:'512 visits · 深度',close:'關閉',loadModel:'載入模型'},'zh-Hans':{lineTool:'线段',arrowTool:'箭头',fastBudget:'32 visits · 快速',balancedBudget:'128 visits · 均衡',deepBudget:'512 visits · 深度',close:'关闭',loadModel:'加载模型'},en:{lineTool:'Line',arrowTool:'Arrow',fastBudget:'32 visits · Fast',balancedBudget:'128 visits · Balanced',deepBudget:'512 visits · Deep',close:'Close',loadModel:'Load model'},ja:{lineTool:'線',arrowTool:'矢印',fastBudget:'32 visits · 高速',balancedBudget:'128 visits · 標準',deepBudget:'512 visits · 深い探索',close:'閉じる',loadModel:'モデルを読み込む'},ko:{lineTool:'선',arrowTool:'화살표',fastBudget:'32 visits · 빠르게',balancedBudget:'128 visits · 균형',deepBudget:'512 visits · 깊게',close:'닫기',loadModel:'모델 불러오기'}}))Object.assign(I18N[locale],values);
const LANGUAGE_COOKIE = 'ng.language';
const supportedLanguages = ['zh-Hant', 'zh-Hans', 'en', 'ja', 'ko'];
function readCookie(name) {
  const prefix = `${name}=`;
  return document.cookie.split(';').map(value => value.trim()).find(value => value.startsWith(prefix))?.slice(prefix.length) || '';
}
function saveLanguageCookie(value) {
  const secure = location.protocol === 'https:' ? '; Secure' : '';
  document.cookie = `${LANGUAGE_COOKIE}=${encodeURIComponent(value)}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
}
function browserLanguage() {
  for (const raw of navigator.languages?.length ? navigator.languages : [navigator.language || 'en']) {
    const tag = String(raw).toLowerCase();
    if (tag.startsWith('zh')) return /hans|cn|sg/.test(tag) ? 'zh-Hans' : 'zh-Hant';
    if (tag.startsWith('ja')) return 'ja';
    if (tag.startsWith('ko')) return 'ko';
    if (tag.startsWith('en')) return 'en';
  }
  return 'en';
}
function initialLanguage() {
  let stored = '';
  try { stored = decodeURIComponent(readCookie(LANGUAGE_COOKIE)); } catch { stored = ''; }
  if (supportedLanguages.includes(stored)) return stored;
  const legacy = localStorage.getItem(LANGUAGE_COOKIE);
  if (supportedLanguages.includes(legacy)) {
    localStorage.removeItem(LANGUAGE_COOKIE);
    saveLanguageCookie(legacy);
    return legacy;
  }
  return browserLanguage();
}
for(const [locale, values] of Object.entries({
  'zh-Hant': {stonePreview:'選擇材質即時預覽', desktopDownload:'下載桌面版', gpuSecureRequired:'WebGPU 需要 HTTPS', gpuSecureHint:'請透過 HTTPS 或 localhost 開啟。GitHub Pages 會提供 HTTPS。', gpuUnsupportedHint:'此瀏覽器未提供 WebGPU。請使用最新版 Chrome／Edge，並開啟硬體加速。', gpuAdapterHint:'瀏覽器沒有回報可用的 GPU。請檢查硬體加速、GPU 驅動與瀏覽器權限。'},
  'zh-Hans': {stonePreview:'选择材质实时预览', desktopDownload:'下载桌面版', gpuSecureRequired:'WebGPU 需要 HTTPS', gpuSecureHint:'请通过 HTTPS 或 localhost 打开。GitHub Pages 会提供 HTTPS。', gpuUnsupportedHint:'此浏览器未提供 WebGPU。请使用最新版 Chrome／Edge，并开启硬件加速。', gpuAdapterHint:'浏览器没有回报可用的 GPU。请检查硬件加速、GPU 驱动和浏览器权限。'},
  en: {stonePreview:'Live stone preview', desktopDownload:'Download desktop', gpuSecureRequired:'WebGPU requires HTTPS', gpuSecureHint:'Open this page over HTTPS or localhost. GitHub Pages provides HTTPS.', gpuUnsupportedHint:'This browser does not expose WebGPU. Use a current Chrome or Edge release and enable hardware acceleration.', gpuAdapterHint:'The browser did not find a usable GPU. Check hardware acceleration, GPU drivers, and browser policy.'},
  ja: {stonePreview:'素材を選ぶとプレビューします', desktopDownload:'デスクトップ版をダウンロード', gpuSecureRequired:'WebGPUにはHTTPSが必要です', gpuSecureHint:'HTTPSまたはlocalhostで開いてください。GitHub PagesはHTTPSを提供します。', gpuUnsupportedHint:'このブラウザーではWebGPUを利用できません。最新版のChrome／Edgeとハードウェアアクセラレーションをお試しください。', gpuAdapterHint:'利用可能なGPUが見つかりません。ハードウェアアクセラレーション、GPUドライバー、ブラウザーポリシーを確認してください。'},
  ko: {stonePreview:'소재를 선택하면 미리 볼 수 있습니다', desktopDownload:'데스크톱 버전 다운로드', gpuSecureRequired:'WebGPU에는 HTTPS가 필요합니다', gpuSecureHint:'HTTPS 또는 localhost로 접속하세요. GitHub Pages는 HTTPS를 제공합니다.', gpuUnsupportedHint:'이 브라우저에서는 WebGPU를 사용할 수 없습니다. 최신 Chrome／Edge와 하드웨어 가속을 사용하세요.', gpuAdapterHint:'사용 가능한 GPU를 찾지 못했습니다. 하드웨어 가속, GPU 드라이버, 브라우저 정책을 확인하세요.'}
})) Object.assign(I18N[locale], values);
let language = initialLanguage();
const savedPrefs = readStore('ng.preferences', null);
let prefs = Object.assign({board:savedPrefs?'wood':'night',stones:savedPrefs?'classic':'moon',size:19,font:15,sound:'01',motion:'full',theme:'dark'}, savedPrefs || {});
let pendingLinePoint=null;
let collectionTrees=[], root, current, board = [], captures = {[BLACK]:0,[WHITE]:0}, toPlay = BLACK, last = null, path = [], positionHistory=[], dirty=false, pointer=null, animationFrame=0, library=readStore('ng.library',[]), pendingInstall, engineWorker=null, activeModelId='', engineBoardSize=0, engineReady=false, analyzedNode=null, analyzedBoard=null, ownershipMap=null, engineRequestId=0;
let animationTimer = 0, gpuState = 'unknown', modelAvailable = false;
const skyStartedAt = performance.now() / 1000;
const treePan = {x:0, y:0, width:320, height:240, root:null, dragging:false, moved:false, lastX:0, lastY:0};
const modelDb = () => new Promise((resolve,reject)=>{const req=indexedDB.open('nightygo-models-v1',1);req.onupgradeneeded=()=>req.result.createObjectStore('models',{keyPath:'id'});req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)});
async function putModel(model){const db=await modelDb();return new Promise((resolve,reject)=>{const tx=db.transaction('models','readwrite');tx.objectStore('models').put(model);tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error)})}
async function getModel(id){const db=await modelDb();return new Promise((resolve,reject)=>{const req=db.transaction('models').objectStore('models').get(id);req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function listModels(){const db=await modelDb();return new Promise((resolve,reject)=>{const req=db.transaction('models').objectStore('models').getAll();req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
function engineRequest(type,payload={}){return new Promise((resolve,reject)=>{if(!engineWorker)engineWorker=new Worker(new URL('./engine-worker.js',import.meta.url));const worker=engineWorker,requestId=++engineRequestId;const cleanup=()=>{worker.removeEventListener('message',onMessage);worker.removeEventListener('error',onError);worker.removeEventListener('messageerror',onMessageError)};const onMessage=event=>{if(event.data.requestId!==requestId)return;cleanup();if(event.data.type==='error')reject(Error(event.data.message));else resolve(event.data.result)};const onError=event=>{cleanup();reject(Error(event.message||'KataGo worker failed to start'))};const onMessageError=()=>{cleanup();reject(Error('Could not read the KataGo worker response'))};worker.addEventListener('message',onMessage);worker.addEventListener('error',onError);worker.addEventListener('messageerror',onMessageError);try{worker.postMessage({type,requestId,...payload},payload.bytes?[payload.bytes]:[])}catch(error){cleanup();reject(error)}})}
function movesForPath(nodes=path){const rootProps=nodes[0]?.props||{};if(rootProps.AW||rootProps.AE||nodes.slice(1).some(n=>n.props?.AB||n.props?.AW||n.props?.AE))throw Error('AI 暫不支援變化中的棋盤編輯與白子初始設定；一般對局和標準黑棋讓子可分析。');const setup=expandSetup(rootProps.AB,boardSize());if(setup.length===1)throw Error('AI 僅支援標準兩子以上讓子設定。');return [...setup.map(([x,y])=>({loc:y*boardSize()+x,color:BLACK})),...nodes.flatMap(node=>{const p=node.props||{};const color=p.B?BLACK:p.W?WHITE:null;if(!color)return[];const value=(p.B||p.W)[0];return [{loc:value===''?-1:(value.charCodeAt(1)-97)*boardSize()+value.charCodeAt(0)-97,color}]})]}
async function refreshModels(){const models=await listModels();modelAvailable=models.length>0;const select=$('#model-select');select.innerHTML=models.length?models.map(m=>`<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)} · ${(m.size/1048576).toFixed(1)} MB</option>`).join(''):'<option value="">尚未匯入模型</option>';if(activeModelId&&models.some(m=>m.id===activeModelId))select.value=activeModelId;else if(models.length)select.value=models[0].id;const memory=navigator.deviceMemory||4;const tier=memory<4?0:memory<8?1:2;const advice={'zh-Hant':`裝置記憶體粗估 ${memory} GB，建議${['輕量','平衡','高強度'][tier]}模型。此數字僅為瀏覽器估值；棋盤尺寸與可用 GPU 記憶體也會影響載入。模型只存在本機瀏覽器。`,'zh-Hans':`设备内存粗估 ${memory} GB，建议${['轻量','均衡','高强度'][tier]}模型。该数字仅为浏览器估值；棋盘大小和 GPU 可用内存也会影响加载。模型只保存在本地浏览器。`,en:`Estimated device memory: ${memory} GB. Suggested tier: ${['light','balanced','strong'][tier]}. This browser estimate is approximate; board size and GPU memory also affect model loading. Models stay in this browser.`,ja:`端末メモリーの推定は ${memory} GB。おすすめ：${['軽量','標準','高性能'][tier]}モデル。ブラウザーによる概算で、盤サイズとGPUメモリーも読み込みに影響します。モデルはこのブラウザーに保存されます。`,ko:`기기 메모리 추정치 ${memory} GB. 추천 모델: ${['경량','균형','고성능'][tier]}. 브라우저 추정값이며 바둑판 크기와 GPU 메모리도 로딩에 영향을 줍니다. 모델은 이 브라우저에 저장됩니다.`};$('#model-advice').textContent=advice[language]||advice.en;refreshAiSetup()}
function storedAiConfig(){try{const value=localStorage.getItem('ng.ai-profile');return value?validateAiConfig(JSON.parse(value)):null}catch{return null}}
function refreshAiSetup(){const config=storedAiConfig();const modelReady=modelAvailable||Boolean(activeModelId);$('#ai-model-status').textContent=modelReady?tr('setupReady'):tr('setupMissing');$('#ai-profile-status').textContent=config?tr('setupReady'):tr('setupMissing');$('#ai-model-status').className=modelReady?'is-ready':'is-missing';$('#ai-profile-status').className=config?'is-ready':'is-missing';$('#ai-setup-message').textContent=gpuState==='available'&&!config?tr('gpuReadySetupPrompt'):gpuState==='available'&&!modelReady?tr('gpuReadyModelPrompt'):gpuState==='available'?tr('gpuReadyComplete'):tr('gpuBeforeSetup');$('#ai-config-status').textContent=config?tr('profileReady'):tr('profileMissing');$('#export-ai-config').disabled=!config;if(config){$('#search-visits').value=String(config.searchVisits);$('#search-time').value=String(config.maxSearchTimeMs)}}
function saveAiConfig(config){const valid=validateAiConfig(config);localStorage.setItem('ng.ai-profile',JSON.stringify(valid));refreshAiSetup();return valid}
function downloadAiConfig(){const config=saveAiConfig({format:DEFAULT_AI_CONFIG.format,version:DEFAULT_AI_CONFIG.version,searchVisits:Number($('#search-visits').value),maxSearchTimeMs:Number($('#search-time').value)});const blob=new Blob([JSON.stringify(config,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='nightygo-ai-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
async function importAiConfig(file){if(!file)return;const config=parseAiConfig(await file.text());saveAiConfig(config);toast(tr('profileImported'))}
async function openModelCenter(){await refreshModels();$('#model-dialog').showModal()}
async function importModel(file){if(!file)return;if(!file.name.endsWith('.bin.gz'))throw Error('請選擇 KataGo .bin.gz 網路檔');const bytes=await file.arrayBuffer();if(bytes.byteLength<1024||new Uint8Array(bytes,0,2)[0]!==31||new Uint8Array(bytes,0,2)[1]!==139)throw Error('這不是有效的 gzip 模型檔');const model={id:crypto.randomUUID?.()||`${Date.now()}-${Math.random()}`,name:file.name,size:bytes.byteLength,bytes,added:Date.now()};await putModel(model);activeModelId=model.id;await refreshModels();toast('模型已儲存於本機瀏覽器')}
async function loadSelectedModel(){const id=$('#model-select').value;if(!id)throw Error(tr('needModel'));const config=storedAiConfig();if(!config)throw Error(tr('needProfile'));const model=await getModel(id);if(!model)throw Error(tr('modelNotFound'));if(engineWorker)engineWorker.terminate();engineWorker=null;engineReady=false;$('#analyze-position').disabled=true;$('#play-ai').disabled=true;$('#review-game').disabled=true;const loaded=await engineRequest('load',{bytes:model.bytes.slice(0),size:boardSize()});activeModelId=id;engineBoardSize=boardSize();engineReady=true;analyzedNode=null;$('#gpu-status').textContent=loaded.gpu?'KataGo · WebGPU':'KataGo · CPU';$('#gpu-status').classList.add('ready');$('#engine-message').textContent=`KataGo v${loaded.version} 已載入。推論在本機執行；${loaded.gpu?'使用 WebGPU。':'此裝置使用 CPU，分析可能較慢。'}`;$('#analyze-position').disabled=false;$('#play-ai').disabled=false;$('#review-game').disabled=false;refreshAiSetup();$('#model-dialog').close();toast('KataGo 模型已載入')}
async function analyzePosition(){const target=current,targetBoard=board,targetPlayer=toPlay,targetKomi=Number(root.props.KM?.[0]||7.5);try{const result=await engineRequest('analyze',{moves:movesForPath(),toPlay:targetPlayer,komi:targetKomi});if(current!==target||board!==targetBoard||toPlay!==targetPlayer||Number(root.props.KM?.[0]||7.5)!==targetKomi)return;analyzedNode=target;analyzedBoard=targetBoard;ownershipMap=result.ownership;drawBoard();$('#ai-empty').hidden=true;$('#analysis-results').hidden=false;$('#visits').textContent='神經網路推論';const win=result.value[toPlay===WHITE?0:1];$('#winrate').textContent=`${(win*100).toFixed(1)}%`;$('#score-lead').textContent=`${result.value[4]>=0?'+':''}${result.value[4].toFixed(1)} 白方目差`;$('#candidate-list').innerHTML=result.candidates.filter(c=>{if(c.loc===boardSize()*boardSize())return true;const x=c.loc%boardSize(),y=Math.floor(c.loc/boardSize());if(board[y]?.[x])return false;try{const ko=last&&!last.pass&&positionHistory.length>1?positionHistory.at(-2):null;applyMove(board,toPlay,x,y,true,ko);return true}catch{return false}}).slice(0,6).map(c=>`<li>${c.loc===boardSize()*boardSize()?'Pass':`${'ABCDEFGHJKLMNOPQRST'[c.loc%boardSize()]}${boardSize()-(c.loc/boardSize()|0)}`}</li>`).join('');}catch(error){toast(error.message)}}
async function playAiMove(){const target=current,targetBoard=board,targetPlayer=toPlay,targetKomi=Number(root.props.KM?.[0]||7.5);try{const config=storedAiConfig();if(!config)throw Error(tr('needProfile'));const result=await engineRequest('search',{moves:movesForPath(),toPlay:targetPlayer,komi:targetKomi,visits:config.searchVisits,maxSearchTimeMs:config.maxSearchTimeMs});if(current!==target||board!==targetBoard||toPlay!==targetPlayer||Number(root.props.KM?.[0]||7.5)!==targetKomi)return;const loc=result.best;if(loc<0)appendMove(0,0,true);else appendMove(loc%boardSize(),Math.floor(loc/boardSize()));toast(`AI 搜尋 ${result.visits} 次 · ${Math.round(result.winrate*100)}%`)}catch(error){toast(error.message)}}
async function reviewGame(){if(!engineWorker){toast('請先載入 KataGo 模型');return}const line=[root];while(line.at(-1).children?.length)line.push(line.at(-1).children[0]);if(line.length>251){toast('整盤覆盤目前最多處理 250 手');return}const findings=[];for(let i=0;i<line.length;i++){const chain=[];let n=line[i];while(n){chain.unshift(n);n=n._parent||null}/* parent links are created during parse below; fall back to main-line prefix */const nodes=line.slice(0,i+1);const moves=movesForPath(nodes);const side=nodes.slice(1).reduce((p,node)=>node.props.B?WHITE:node.props.W?BLACK:p, nodes[0].props.PL?.[0]==='W'?WHITE:BLACK);try{const value=await engineRequest('analyze',{moves,toPlay:side,komi:Number(root.props.KM?.[0]||7.5)});findings.push({move:i,wr:value.value[0]});}catch(e){toast(e.message);return}if(i%10===0)$('#engine-message').textContent=`整盤覆盤中：${i}/${line.length-1}`}
 const swings=findings.slice(1).map((x,i)=>({...x,swing:Math.abs(x.wr-findings[i].wr)})).filter(x=>x.swing>.12).sort((a,b)=>b.swing-a.swing).slice(0,8);$('#analysis-results').hidden=false;$('#ai-empty').hidden=true;$('#candidate-list').innerHTML=swings.length?swings.map(x=>`<li><button class="review-jump" data-move="${x.move}">第 ${x.move} 手 · 勝率變化 ${(x.swing*100).toFixed(1)}%</button></li>`).join(''):'<li>主線各手勝率已計算，未發現大於 12% 的變化。</li>';document.querySelectorAll('.review-jump').forEach(b=>b.onclick=()=>navigateTo(line[Number(b.dataset.move)]));$('#engine-message').textContent=`完成 ${findings.length-1} 手主線覆盤；點擊列表可跳到變化較大的手。`}
function tr(key){return I18N[language]?.[key] || I18N.en[key] || key}
function readStore(key,fallback){try{return JSON.parse(localStorage.getItem(key)) ?? fallback}catch{return fallback}}
function writeStore(key,value){try{localStorage.setItem(key,JSON.stringify(value))}catch{toast('Storage limit reached; export your SGF to keep a copy.')}}
function applyLanguage(){document.documentElement.lang=language;document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=tr(el.dataset.i18n));$('#language').value=language;$('#library-search').placeholder=tr('librarySearch');if($('#ai-setup-message'))refreshAiSetup()}
function openMailDialog(){const input=$('#mail-address');input.value=localStorage.getItem('ng.mail-address')||'';$('#mail-dialog').showModal();input.focus()}
function sendGameMail(){const input=$('#mail-address'),form=$('#mail-dialog form');if(!form.reportValidity())return;const address=input.value.trim();if(!address)return;localStorage.setItem('ng.mail-address',address);const sgf=serializeCollection();const subject=tr('mailSubject'),body=`${tr('mailBody')}\n\n${sgf}`;const url=`mailto:${encodeURIComponent(address)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;if(url.length>7000){toast(tr('mailTooLarge'));return}$('#mail-dialog').close();window.location.href=url}
function makeRoot(size=19){return {props:{GM:['1'],FF:['4'],CA:['UTF-8'],AP:['NightyGo Web:0.1'],SZ:[String(size)],KM:['6.5']},children:[]}}
function setupNew(size=Number(prefs.size)){if(root&&dirty)saveLibrary(false);root=makeRoot(size);collectionTrees=[root];current=root;path=[root];dirty=false;rebuild();refresh();writeStore('ng.autosave',serializeCollection())}
function boardSize(){let value=root?.props?.SZ?.[0]||'19';if(value.includes(':'))value=value.split(':')[0];return Math.max(2,Math.min(25,Number(value)||19))}
function emptyBoard(size=boardSize()){return Array.from({length:size},()=>Array(size).fill(0))}
function neighbors(x,y,n){return [[x-1,y],[x+1,y],[x,y-1],[x,y+1]].filter(([a,b])=>a>=0&&b>=0&&a<n&&b<n)}
function groupInfo(grid,x,y){const color=grid[y][x],group=[],lib=new Set(),seen=new Set([`${x},${y}`]),stack=[[x,y]];while(stack.length){const [cx,cy]=stack.pop();group.push([cx,cy]);for(const [nx,ny] of neighbors(cx,cy,grid.length)){if(grid[ny][nx]===0)lib.add(`${nx},${ny}`);else if(grid[ny][nx]===color&&!seen.has(`${nx},${ny}`)){seen.add(`${nx},${ny}`);stack.push([nx,ny])}}}return {group,lib}}
function applyMove(grid,color,x,y,checkKo=false,previous=null){const n=grid.length;if(x<0||y<0||x>=n||y>=n||grid[y][x])throw Error(tr('illegal'));const next=grid.map(r=>r.slice());next[y][x]=color;let captured=[];for(const [nx,ny] of neighbors(x,y,n)){if(next[ny][nx]===3-color){const g=groupInfo(next,nx,ny);if(!g.lib.size){captured.push(...g.group);for(const [gx,gy] of g.group)next[gy][gx]=0}}}if(!groupInfo(next,x,y).lib.size)throw Error(tr('illegal'));if(checkKo&&previous&&sameBoard(next,previous))throw Error(tr('illegal'));return {grid:next,captured}}
function sameBoard(a,b){return a.length===b.length&&a.every((r,y)=>r.every((v,x)=>v===b[y][x]))}
function decodePoint(value,n){if(value.length!==2)throw Error('Invalid SGF coordinate');const x=value.charCodeAt(0)-97,y=value.charCodeAt(1)-97;if(x<0||y<0||x>=n||y>=n)throw Error('SGF coordinate outside board');return [x,y]}
function expandSetup(vals,n){const out=[];for(const val of vals||[]){if(val.includes(':')){const [a,b]=val.split(':').map(v=>decodePoint(v,n));for(let y=Math.min(a[1],b[1]);y<=Math.max(a[1],b[1]);y++)for(let x=Math.min(a[0],b[0]);x<=Math.max(a[0],b[0]);x++)out.push([x,y])}else out.push(decodePoint(val,n))}return out}
function rebuild(){board=emptyBoard();captures={[BLACK]:0,[WHITE]:0};toPlay=BLACK;last=null;positionHistory=[board];for(const node of path){const p=node.props||{};let hadSetup=false;for(const [key,val] of [['AE',0],['AB',BLACK],['AW',WHITE]])for(const [x,y] of expandSetup(p[key],boardSize())){board[y][x]=val;hadSetup=true}if(hadSetup)positionHistory=[board];if(p.PL?.[0])toPlay=p.PL[0]==='W'?WHITE:BLACK;if(p.B||p.W){const color=p.B?BLACK:WHITE;toPlay=color;const value=(p.B||p.W)[0];if(value===''||(value==='tt'&&boardSize()<=19)){last={color,x:null,y:null,pass:true};toPlay=3-color;positionHistory.push(board);continue}const [x,y]=decodePoint(value,boardSize());const result=applyMove(board,color,x,y);board=result.grid;captures[color]+=result.captured.length;last={color,x,y};toPlay=3-color;positionHistory.push(board)}}}
function appendMove(x,y,pass=false){if(path.length>2){const p1=path.at(-1).props,p2=path.at(-2).props;if((p1.B?.[0]===''||p1.W?.[0]==='')&&(p2.B?.[0]===''||p2.W?.[0]==='')){toast(tr('gameOver'));return}}const color=toPlay,props={};props[color===BLACK?'B':'W']=[pass?'':String.fromCharCode(97+x)+String.fromCharCode(97+y)];const node={props,children:[]};current.children.push(node);current=node;path.push(node);dirty=true;rebuild();if(!pass)playSound(prefs.sound);refresh()}
function navigateTo(target){const found=[];function search(node){found.push(node);if(node===target)return true;for(const c of node.children||[])if(search(c))return true;found.pop();return false}if(search(root)){path=found;current=target;rebuild();refresh()}}
function previous(){if(path.length>1){path.pop();current=path.at(-1);rebuild();refresh()}}
function next(index=0){if(current.children?.length){const nextNode=current.children[index]||current.children[0];path.push(nextNode);current=nextNode;rebuild();refresh()}else toast(tr('noBranch'))}
function updateComment(value){if(value.trim())current.props.C=[value];else delete current.props.C;dirty=true;refreshTree();writeStore('ng.autosave',serializeCollection())}
function setProp(key,value){if(value==='')delete root.props[key];else root.props[key]=[value];dirty=true;refresh()}
function serialize(node){return serializeSgf(node)}
function serializeCollection(){return collectionTrees.map(serialize).join("\n")}
function downloadSgf(){const data=serializeCollection();const blob=new Blob([data],{type:'application/x-go-sgf;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${safeName(root.props.PB?.[0]||'nightygo')}-${new Date().toISOString().slice(0,10)}.sgf`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);dirty=false;refresh();toast(tr('saved'));saveLibrary(true)}
function handicapPoints(size,count){const star=size===19?[3,9,15]:size===13?[3,6,9]:[2,4,6];const [lo,mid,hi]=star;return [[hi,lo],[lo,hi],[lo,lo],[hi,hi],[mid,mid],[mid,lo],[mid,hi],[lo,mid],[hi,mid]].slice(0,count).map(([x,y])=>String.fromCharCode(97+x)+String.fromCharCode(97+y))}
function scoreGame(){let black=0,white=0,seen=new Set();for(let y=0;y<boardSize();y++)for(let x=0;x<boardSize();x++){if(board[y][x]===BLACK)black++;else if(board[y][x]===WHITE)white++;else if(!seen.has(`${x},${y}`)){const region=[],border=new Set(),stack=[[x,y]];seen.add(`${x},${y}`);while(stack.length){const [cx,cy]=stack.pop();region.push([cx,cy]);for(const [nx,ny]of neighbors(cx,cy,boardSize())){if(board[ny][nx])border.add(board[ny][nx]);else if(!seen.has(`${nx},${ny}`)){seen.add(`${nx},${ny}`);stack.push([nx,ny])}}}if(border.size===1){if(border.has(BLACK))black+=region.length;else white+=region.length}}}white+=Number(root.props.KM?.[0]||7.5);const diff=Math.abs(black-white),result=black>white?`B+${diff.toFixed(1)}`:`W+${diff.toFixed(1)}`;setProp('RE',result);toast(`面積計分估算（未判定死活）：黑 ${black.toFixed(1)} · 白 ${white.toFixed(1)}（含貼目） · ${result}`)}
function safeName(s){return s.toLowerCase().replace(/[^a-z0-9-_]+/g,'-').replace(/^-|-$/g)||'game'}
function saveLibrary(toastIt=true){if(!root)return;const sgf=serializeCollection(),meta=root.props;const title=`${meta.PB?.[0]||'Black'} – ${meta.PW?.[0]||'White'}`;const old=library.find(g=>g.sgf===sgf);library=[{id:old?.id||Date.now(),title,event:meta.EV?.[0]||'',result:meta.RE?.[0]||'',tags:old?.tags||[],sgf,updated:new Date().toISOString()},...library.filter(g=>g.sgf!==sgf)].slice(0,100);writeStore('ng.library',library);writeStore('ng.autosave',sgf);dirty=false;refreshLibrary();refreshHeader();if(toastIt)toast(tr('saveFirst'))}
function loadSgfTree(tree, collection=[tree]){collectionTrees=collection;root=tree;current=root;path=[root];while(current.children?.length){current=current.children[0];path.push(current)}dirty=false;rebuild();refresh();writeStore('ng.autosave',serializeCollection());toast(tr('loaded'))}
function refresh(){if(engineBoardSize&&engineBoardSize!==boardSize()){engineWorker?.terminate();engineWorker=null;engineBoardSize=0;engineReady=false;analyzedNode=null;analyzedBoard=null;ownershipMap=null;$('#analyze-position').disabled=true;$('#play-ai').disabled=true;$('#review-game').disabled=true;$('#engine-message').textContent='棋盤尺寸已變更，請重新載入模型。'}if(analyzedNode&&(analyzedNode!==current||analyzedBoard!==board)){analyzedNode=null;analyzedBoard=null;ownershipMap=null;$('#analysis-results').hidden=true;$('#candidate-list').replaceChildren();$('#ai-empty').hidden=false;if(engineReady)$('#engine-message').textContent='局面已變更，請重新分析。'}refreshBoard();refreshHeader();refreshControls();refreshTree();refreshInfo();refreshLibrary();$('#comment').value=current.props.C?.join('\n')||'';$('#tree-count').textContent=countNodes(root);$('#move-position').textContent=`${path.length-1} / ${countNodes(root)-1}`;$('#undo').disabled=path.length<=1;$('#redo').disabled=!current.children?.length;$('#previous').disabled=path.length<=1;$('#next').disabled=!current.children?.length;if(dirty)writeStore('ng.autosave',serializeCollection())}
function countNodes(node){return 1+(node.children||[]).reduce((a,c)=>a+countNodes(c),0)}
function refreshHeader(){const p=root.props;$('#game-name').textContent=p.GN?.[0]||`${p.PB?.[0]||tr('blackPlayer')}${tr('versus')}${p.PW?.[0]||tr('whitePlayer')}`;$('#game-meta').innerHTML=`${boardSize()} × ${boardSize()} <span>·</span> ${dirty?tr('unsaved'):(p.DT?.[0]||tr('unsaved'))}`}
function refreshControls(){$('#turn-label').textContent=tr(toPlay===BLACK?'blackTurn':'whiteTurn');$('#turn-pill .stone-chip').className=`stone-chip ${toPlay===BLACK?'black':'white'}`;$('#black-captures').textContent=captures[BLACK];$('#white-captures').textContent=captures[WHITE];$('#move-count').textContent=Math.max(0,path.length-1);$('#game-meta').setAttribute('title',dirty?'Unsaved changes':'')}
function refreshInfo(){const p=root.props;$('#info-black').textContent=p.PB?.[0]||'—';$('#info-white').textContent=p.PW?.[0]||'—';$('#info-event').textContent=p.EV?.[0]||'—';$('#info-result').textContent=p.RE?.[0]||'—'}
function refreshLibrary(){const q=$('#library-search').value.toLocaleLowerCase();const found=library.filter(g=>(g.title+' '+g.event+' '+g.result+' '+(g.tags||[]).join(' ')).toLocaleLowerCase().includes(q));$('#library-list').innerHTML=found.length?found.map(g=>`<article class="library-card" data-lib="${g.id}"><b>${escapeHtml(g.title)}</b><span>${escapeHtml(g.event||'Local SGF')} · ${escapeHtml(g.result||'—')}</span><input class="library-tags" data-tags="${g.id}" value="${escapeHtml((g.tags||[]).join(', '))}" placeholder="tags, separated by commas" aria-label="Tags" /></article>`).join(''):`<div class="library-empty">${tr('noGames')}</div>`;document.querySelectorAll('[data-lib]').forEach(el=>el.onclick=e=>{if(e.target.matches('.library-tags'))return;const g=library.find(v=>v.id===Number(el.dataset.lib));if(g)try{const games=parseSgf(g.sgf);loadSgfTree(games[0],games)}catch{toast(tr('badSgf'))}});document.querySelectorAll('.library-tags').forEach(input=>input.onchange=()=>{const g=library.find(v=>v.id===Number(input.dataset.tags));if(g){g.tags=input.value.split(',').map(t=>t.trim()).filter(Boolean);writeStore('ng.library',library);toast('標籤已儲存')}})}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function refreshTree() {
  const svg = $('#game-tree');
  const viewport = $('#tree-scroll');
  const mainOnly = $('#main-line').classList.contains('active');
  if (treePan.root !== root) {
    treePan.root = root;
    treePan.x = 0;
    treePan.y = 0;
  }
  const width = Math.max(260, viewport.clientWidth || 320);
  const height = Math.max(180, viewport.clientHeight || 240);
  treePan.width = width;
  treePan.height = height;
  svg.innerHTML = '';
  svg.setAttribute('width', width);
  svg.setAttribute('height', height);
  svg.setAttribute('viewBox', `${treePan.x} ${treePan.y} ${width} ${height}`);
  svg.style.width = '100%';
  svg.style.height = '100%';

  const nodes = [];
  const edges = [];
  let maxY = 0;
  function layout(node, x, y) {
    nodes.push({node, x, y});
    maxY = Math.max(maxY, y);
    for (const [index, child] of (node.children || []).entries()) {
      if (mainOnly && index > 0) continue;
      const childX = index === 0 ? x : x + index + 1;
      edges.push({from: {x, y}, to: {x: childX, y: y + 1}, active: path.includes(node) && path.includes(child)});
      layout(child, childX, y + 1);
    }
  }
  layout(root, 0, 0);

  const stepX = 62, stepY = 35, pad = 26;
  const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  background.setAttribute('class', 'tree-pan-surface');
  background.setAttribute('x', treePan.x);
  background.setAttribute('y', treePan.y);
  background.setAttribute('width', width);
  background.setAttribute('height', height);
  svg.append(background);
  for (const edge of edges) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const x1 = pad + edge.from.x * stepX, y1 = pad + edge.from.y * stepY;
    const x2 = pad + edge.to.x * stepX, y2 = pad + edge.to.y * stepY;
    line.setAttribute('d', x1 === x2 ? `M ${x1} ${y1 + 8} L ${x2} ${y2 - 8}` : `M ${x1} ${y1 + 8} C ${x1} ${y1 + 19}, ${x2} ${y2 - 19}, ${x2} ${y2 - 8}`);
    line.setAttribute('class', `tree-link ${edge.active ? 'active' : ''}`);
    svg.append(line);
  }
  for (const item of nodes) {
    const {node, x, y} = item;
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const color = node.props.B ? 'black' : node.props.W ? 'white' : '';
    group.setAttribute('class', `tree-node ${color} ${current === node ? 'current' : ''}`);
    group.setAttribute('transform', `translate(${pad + x * stepX},${pad + y * stepY})`);
    group.setAttribute('role', 'treeitem');
    group.setAttribute('tabindex', '0');
    group.innerHTML = color ? `<circle r="8"></circle><text x="12" y="4">${y}</text>` : '<rect x="-5" y="-5" width="10" height="10" rx="2" fill="#71829f" stroke="none"></rect>';
    group.onclick = () => navigateTo(node);
    group.onkeydown = event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); navigateTo(node); }
    };
    svg.append(group);
  }
  $('#variation-count').innerHTML = `${countBranches(root)} ${tr('variations')}`;
}
function bindTreePan() {
  const svg = $('#game-tree');
  svg.addEventListener('pointerdown', event => {
    if (event.target.closest?.('.tree-node') || event.button !== 0) return;
    treePan.dragging = true;
    treePan.moved = false;
    treePan.lastX = event.clientX;
    treePan.lastY = event.clientY;
    svg.classList.add('is-panning');
    svg.setPointerCapture(event.pointerId);
  });
  svg.addEventListener('pointermove', event => {
    if (!treePan.dragging) return;
    const dx = event.clientX - treePan.lastX;
    const dy = event.clientY - treePan.lastY;
    if (Math.abs(dx) + Math.abs(dy) > 1) treePan.moved = true;
    treePan.x -= dx;
    treePan.y -= dy;
    treePan.lastX = event.clientX;
    treePan.lastY = event.clientY;
    svg.setAttribute('viewBox', `${treePan.x} ${treePan.y} ${treePan.width} ${treePan.height}`);
    const background = svg.querySelector('.tree-pan-surface');
    if (background) { background.setAttribute('x', treePan.x); background.setAttribute('y', treePan.y); }
  });
  const stop = event => {
    if (!treePan.dragging) return;
    treePan.dragging = false;
    svg.classList.remove('is-panning');
    if (svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
  };
  svg.addEventListener('pointerup', stop);
  svg.addEventListener('pointercancel', stop);
}
function countBranches(node){let count=Math.max(0,(node.children?.length||0)-1);for(const child of node.children||[])count+=countBranches(child);return count}
function refreshBoard(){drawBoard();}
function resizeCanvas(){const canvas=$('#go-board'),rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;if(!rect.width||!rect.height)return;const w=Math.round(rect.width*dpr),h=Math.round(rect.height*dpr);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}drawBoard()}
function drawBoard() {
  const canvas = $('#go-board');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const width = canvas.width, height = canvas.height;
  if (!width || !height) return;
  const size = boardSize();
  const pad = width * 0.063;
  const step = (width - pad * 2) / (size - 1);
  const elapsed = performance.now() / 1000 - skyStartedAt;
  if (prefs.board === 'wood') {
    const background = ctx.createLinearGradient(0, 0, width, height);
    background.addColorStop(0, '#e8c887');
    background.addColorStop(.48, '#d3ad6e');
    background.addColorStop(1, '#c59a58');
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, width, height);
    for (let index = 0; index < 105; index++) {
      const y = (index * 43) % height;
      ctx.strokeStyle = `rgba(85,51,20,${.035 + (index % 4) * .009})`;
      ctx.lineWidth = Math.max(1, width * .001);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.bezierCurveTo(width * .28, y + Math.sin(index) * width * .013,
        width * .72, y + Math.cos(index * .6) * width * .01,
        width, y + Math.sin(index * 1.4) * width * .008);
      ctx.stroke();
    }
  } else {
    ctx.drawImage(getBoardTexture(prefs.board), 0, 0, width, height);
    drawAnimatedSky(ctx, width, elapsed);
  }
  const lineColor = prefs.board === 'wood' ? 'rgba(64,44,25,.85)' : 'rgba(203,219,245,.68)';
  ctx.strokeStyle = lineColor;
  ctx.lineWidth = Math.max(1.2, width * .0015);
  for (let index = 0; index < size; index++) {
    const point = pad + index * step;
    ctx.beginPath(); ctx.moveTo(pad, point); ctx.lineTo(width - pad, point); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(point, pad); ctx.lineTo(point, height - pad); ctx.stroke();
  }
  if ([9, 13, 19].includes(size)) {
    const stars = size === 19 ? [3, 9, 15] : size === 13 ? [3, 6, 9] : [2, 4, 6];
    ctx.fillStyle = lineColor;
    for (const x of stars) for (const y of stars) {
      ctx.beginPath(); ctx.arc(pad + x * step, pad + y * step, Math.max(2.4, width * .004), 0, Math.PI * 2); ctx.fill();
    }
  }
  if (ownershipMap?.length === size * size) {
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const owner = ownershipMap[y * size + x];
      if (Math.abs(owner) <= .2) continue;
      ctx.fillStyle = owner > 0 ? `rgba(100,170,255,${Math.min(.48, Math.abs(owner) * .5)})` : `rgba(255,145,95,${Math.min(.48, Math.abs(owner) * .5)})`;
      ctx.beginPath(); ctx.arc(pad + x * step, pad + y * step, step * .14, 0, Math.PI * 2); ctx.fill();
    }
  }
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    if (board[y]?.[x]) paintStone(ctx, pad + x * step, pad + y * step, step * .455, board[y][x]);
  }
  drawMarkups(ctx, pad, step);
  if (last && !last.pass) {
    const x = pad + last.x * step, y = pad + last.y * step;
    ctx.strokeStyle = last.color === BLACK ? '#f7e0ad' : '#283244';
    ctx.lineWidth = Math.max(1.2, width * .0024);
    ctx.beginPath(); ctx.arc(x, y, step * .19, 0, Math.PI * 2); ctx.stroke();
  }
  if ($('#markup-tool')?.value === 'none' && pointer && pointer.x >= 0 && pointer.y >= 0 && pointer.x < size && pointer.y < size && !board[pointer.y]?.[pointer.x]) {
    ctx.globalAlpha = .46;
    paintStone(ctx, pad + pointer.x * step, pad + pointer.y * step, step * .455, toPlay);
    ctx.globalAlpha = 1;
  }
  scheduleAmbientFrame();
}
const boardTextureCache = new Map();
function getBoardTexture(material) {
  if (boardTextureCache.has(material)) return boardTextureCache.get(material);
  const size = 512;
  const texture = document.createElement('canvas');
  texture.width = texture.height = size;
  const ctx = texture.getContext('2d');
  let seed = material === 'starfield' ? 951 : 461;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const paintNebula = (x, y, color) => {
    const [red, green, blue] = color;
    const glow = ctx.createRadialGradient(x, y, 0, x, y, 170);
    glow.addColorStop(0, `rgba(${red},${green},${blue},.37)`);
    glow.addColorStop(1, `rgba(${red},${green},${blue},0)`);
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, 170, 0, Math.PI * 2); ctx.fill();
  };
  if (material === 'starfield') {
    ctx.fillStyle = '#080d22'; ctx.fillRect(0, 0, size, size);
    paintNebula(120, 175, [68, 43, 136]); paintNebula(360, 345, [21, 75, 114]);
    const radii = [.6, .6, .6, 1, 1, 1, 1.6, 2.2];
    const colors = ['#dce8ff', '#a9c8ff', '#f3d8a5', '#e6c5ff'];
    for (let index = 0; index < 620; index++) {
      const x = random() * size, y = random() * size;
      ctx.fillStyle = colors[Math.floor(random() * colors.length)];
      ctx.beginPath(); ctx.arc(x, y, radii[Math.floor(random() * radii.length)], 0, Math.PI * 2); ctx.fill();
    }
  } else {
    const sky = ctx.createLinearGradient(0, 0, 0, size);
    sky.addColorStop(0, '#101b3b'); sky.addColorStop(.53, '#263b63'); sky.addColorStop(1, '#111a35');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, size, size);
    paintNebula(155, 328, [55, 108, 131]); paintNebula(374, 245, [106, 71, 124]);
    for (let index = 0; index < 280; index++) {
      ctx.fillStyle = '#d7e6ff';
      ctx.beginPath(); ctx.arc(random() * size, random() * size, .5 + random(), 0, Math.PI * 2); ctx.fill();
    }
    ctx.fillStyle = 'rgba(245,227,178,.1)'; ctx.strokeStyle = 'rgba(245,227,178,.27)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(393, 104, 35, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  }
  boardTextureCache.set(material, texture);
  return texture;
}
function drawAnimatedSky(ctx, side, elapsed) {
  const speed = prefs.motion === 'subtle' ? .55 : 1.65;
  const phase = elapsed * speed;
  const starfield = prefs.board === 'starfield';
  const glowColors = starfield ? [[108, 77, 255, 112], [24, 191, 235, 86]] : [[43, 177, 223, 102], [184, 94, 218, 78]];
  for (let index = 0; index < glowColors.length; index++) {
    const [red, green, blue, alpha] = glowColors[index];
    const angle = phase * (index === 0 ? .8 : -.57) + index * 2.5;
    const x = side * (.5 + .3 * Math.cos(angle));
    const y = side * (.5 + .27 * Math.sin(angle));
    const radius = side * .36;
    const glow = ctx.createRadialGradient(x, y, 0, x, y, radius);
    glow.addColorStop(0, `rgba(${red},${green},${blue},${alpha / 255})`);
    glow.addColorStop(1, `rgba(${red},${green},${blue},0)`);
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, side, side);
  }
  const ribbonColors = starfield ? [[67, 232, 225], [175, 89, 255]] : [[100, 212, 244], [201, 123, 235]];
  for (let index = 0; index < ribbonColors.length; index++) {
    const [red, green, blue] = ribbonColors[index];
    const angle = phase * (index === 0 ? .7 : -.52) + index * 2.1;
    const baseY = .38 + index * .23 + .13 * Math.sin(angle);
    const p1 = baseY - .2 * Math.cos(angle);
    const p2 = baseY + .18 * Math.sin(angle + 1.2);
    const p3 = baseY - .14 * Math.cos(angle + .8);
    ctx.beginPath();
    ctx.moveTo(-side * .12, side * baseY);
    ctx.bezierCurveTo(side * .25, side * p1, side * .68, side * p2, side * 1.12, side * p3);
    ctx.lineCap = 'round';
    ctx.strokeStyle = `rgba(${red},${green},${blue},.035)`;
    ctx.lineWidth = side * .105; ctx.stroke();
    ctx.strokeStyle = `rgba(${red},${green},${blue},.094)`;
    ctx.lineWidth = side * .043; ctx.stroke();
    ctx.strokeStyle = 'rgba(218,250,255,.255)';
    ctx.lineWidth = Math.max(1, side * .0045); ctx.stroke();
  }
  const meteorProgress = (elapsed % 24) / 24;
  if (meteorProgress < .22) {
    const travel = meteorProgress / .22;
    const x = side * (-.12 + travel * 1.24);
    const y = side * (.12 + travel * .64);
    const fade = Math.min(1, travel / .12, (1 - travel) / .12);
    ctx.lineCap = 'round';
    ctx.strokeStyle = `rgba(160,203,255,${.29 * fade})`;
    ctx.lineWidth = Math.max(2, side * .009);
    ctx.beginPath(); ctx.moveTo(x - side * .11, y - side * .055); ctx.lineTo(x, y); ctx.stroke();
    ctx.fillStyle = `rgba(255,255,255,${.92 * fade})`;
    ctx.beginPath(); ctx.arc(x, y, Math.max(1.5, side * .004), 0, Math.PI * 2); ctx.fill();
  }
  for (let index = 0; index < 42; index++) {
    const x = (index * .61803398875) % 1;
    const y = (index * .75487766625 + .17) % 1;
    const twinkle = (1 + Math.sin(phase * 3.2 + index * 2.13)) / 2;
    ctx.fillStyle = `rgba(230,239,255,${(25 + twinkle * 220) / 255})`;
    ctx.beginPath(); ctx.arc(x * side, y * side, .7 + twinkle * 1.2, 0, Math.PI * 2); ctx.fill();
  }
}
function scheduleAmbientFrame() {
  if (prefs.board === 'wood' || prefs.motion === 'off' || document.visibilityState !== 'visible') {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    if (animationTimer) clearTimeout(animationTimer);
    animationFrame = 0; animationTimer = 0;
    return;
  }
  if (prefs.motion === 'full' && !animationFrame) {
    animationFrame = requestAnimationFrame(() => { animationFrame = 0; drawBoard(); });
  } else if (prefs.motion === 'subtle' && !animationTimer && !animationFrame) {
    animationTimer = setTimeout(() => { animationTimer = 0; drawBoard(); }, 100);
  }
}
function paintStone(ctx, x, y, radius, color) {
  const gradient = ctx.createRadialGradient(x - radius * .32, y - radius * .4, radius * .06, x, y, radius * 1.15);
  const stops = color === BLACK
    ? prefs.stones === 'star' ? [[0, '#96b9ff'], [.25, '#344a88'], [.72, '#10162d'], [1, '#050812']]
      : prefs.stones === 'moon' ? [[0, '#b6c5d5'], [.3, '#566273'], [.8, '#202630'], [1, '#080b10']]
        : [[0, '#727985'], [.22, '#333842'], [.75, '#111319'], [1, '#050609']]
    : prefs.stones === 'star' ? [[0, '#fff'], [.25, '#d9e5ff'], [.7, '#a5b9e8'], [1, '#5e6f9c']]
      : prefs.stones === 'moon' ? [[0, '#fff'], [.25, '#e3ded2'], [.75, '#a59d8a'], [1, '#716c62']]
        : [[0, '#fff'], [.28, '#f2f3f3'], [.8, '#c8cdd3'], [1, '#9299a4']];
  for (const [offset, shade] of stops) gradient.addColorStop(offset, shade);
  ctx.save();
  ctx.shadowColor = color === BLACK ? '#000a' : '#0006';
  ctx.shadowBlur = radius * .28;
  ctx.shadowOffsetY = radius * .16;
  ctx.fillStyle = gradient;
  ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  ctx.shadowColor = 'transparent';
  if (prefs.stones !== 'classic') {
    ctx.globalAlpha = .24;
    ctx.fillStyle = color === BLACK ? '#b9d6ff' : '#8a7761';
    for (let index = 0; index < 5; index++) {
      ctx.beginPath();
      ctx.arc(x + Math.sin(index * 12.4) * radius * .55, y + Math.cos(index * 7.9) * radius * .5, radius * .035, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
  paintSphereLighting(ctx, x, y, radius);
  ctx.strokeStyle = color === BLACK ? 'rgba(255,255,255,.18)' : 'rgba(50,55,65,.24)';
  ctx.lineWidth = Math.max(.7, radius * .04);
  ctx.beginPath(); ctx.arc(x, y, radius * .96, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
}
function paintSphereLighting(ctx, x, y, radius) {
  ctx.save();
  ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.clip();
  let gradient = ctx.createRadialGradient(x - radius * .4, y - radius * .48, 0, x - radius * .4, y - radius * .48, radius * 1.36);
  gradient.addColorStop(0, 'rgba(255,255,255,.32)');
  gradient.addColorStop(.38, 'rgba(255,255,255,.098)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  gradient = ctx.createRadialGradient(x + radius * .68, y + radius * .7, 0, x + radius * .68, y + radius * .7, radius * 1.12);
  gradient.addColorStop(0, 'rgba(0,0,0,.384)');
  gradient.addColorStop(.52, 'rgba(0,0,0,.118)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  gradient = ctx.createRadialGradient(x - radius * .48, y - radius * .56, 0, x - radius * .48, y - radius * .56, radius * .36);
  gradient.addColorStop(0, 'rgba(255,255,255,.745)');
  gradient.addColorStop(.42, 'rgba(255,255,255,.37)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gradient;
  ctx.beginPath(); ctx.ellipse(x - radius * .45, y - radius * .59, radius * .35, radius * .25, 0, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.49)';
  ctx.lineWidth = Math.max(.7, radius * .05);
  ctx.beginPath(); ctx.arc(x, y, radius * .78, -38 * Math.PI / 180, -143 * Math.PI / 180, true); ctx.stroke();
  ctx.restore();
}
function drawMarkups(ctx,pad,space){const props=current?.props||{},n=boardSize(),ink=prefs.board==='wood'?'#3d2541':'#e5dcff';ctx.save();ctx.lineWidth=Math.max(1.5,space*.07);ctx.strokeStyle=ink;ctx.fillStyle=ink;for(const key of ['LN','AR'])for(const value of props[key]||[]){try{const [from,to]=value.split(':');const [x1,y1]=decodePoint(from,n),[x2,y2]=decodePoint(to,n);const a={x:pad+x1*space,y:pad+y1*space},b={x:pad+x2*space,y:pad+y2*space};ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();if(key==='AR'){const angle=Math.atan2(b.y-a.y,b.x-a.x),r=space*.24;ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-r*Math.cos(angle-.5),b.y-r*Math.sin(angle-.5));ctx.lineTo(b.x-r*Math.cos(angle+.5),b.y-r*Math.sin(angle+.5));ctx.closePath();ctx.fill()}}catch{}}
 for(const key of ['TR','SQ','CR','MA','LB'])for(const value of props[key]||[]){try{const coordinate=key==='LB'?value.slice(0,2):value,[x,y]=decodePoint(coordinate,n),cx=pad+x*space,cy=pad+y*space,r=space*.22;ctx.beginPath();if(key==='TR'){ctx.moveTo(cx,cy-r);ctx.lineTo(cx-r,cy+r);ctx.lineTo(cx+r,cy+r);ctx.closePath();ctx.stroke()}else if(key==='SQ'){ctx.strokeRect(cx-r,cy-r,r*2,r*2)}else if(key==='CR'){ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke()}else if(key==='MA'){ctx.moveTo(cx-r,cy-r);ctx.lineTo(cx+r,cy+r);ctx.moveTo(cx+r,cy-r);ctx.lineTo(cx-r,cy+r);ctx.stroke()}else{ctx.font=`600 ${space*.26}px sans-serif`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(value.slice(3)||'A',cx,cy)}}catch{}}ctx.restore()}
function addMarkup(x,y){const key=$('#markup-tool').value;if(key==='none')return false;const point=String.fromCharCode(97+x)+String.fromCharCode(97+y),property=current.props[key]||[],label=$('#markup-label').value.trim()||'A';if(key==='LN'||key==='AR'){if(!pendingLinePoint){pendingLinePoint=point;toast('請選擇線段的另一個交點');return true}const value=`${pendingLinePoint}:${point}`;pendingLinePoint=null;property.push(value);current.props[key]=property;dirty=true;refresh();return true}const value=key==='LB'?`${point}:${label}`:point,index=property.findIndex(v=>key==='LB'?v.slice(0,2)===point:v===point);if(index>=0)property.splice(index,1);else property.push(value);if(property.length)current.props[key]=property;else delete current.props[key];dirty=true;refresh();return true}
function boardPoint(clientX,clientY){const r=$('#go-board').getBoundingClientRect(),n=boardSize(),pad=r.width*.063,space=(r.width-pad*2)/(n-1);const x=Math.round((clientX-r.left-pad)/space),y=Math.round((clientY-r.top-pad)/space);return {x,y,distance:Math.hypot(clientX-r.left-(pad+x*space),clientY-r.top-(pad+y*space)),n}}
function playSound(which){if(which==='off')return;const audio=new Audio(`assets/sounds/go_stone_${which}.wav`);audio.volume=.55;audio.play().catch(()=>{})}
function playCapture(count){if(!count)return;const key=count===1?'capture_single':count<=3?'capture_small_group':count<=7?'capture_group':'capture_large_group';const a=new Audio(`assets/sounds/${key}.wav`);a.volume=.55;a.play().catch(()=>{})}
let toastTimer;function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2300)}
async function checkGpu(){const tag=$('#gpu-status');tag.textContent=tr('gpuChecking');tag.className='status-tag';if(!globalThis.isSecureContext){gpuState='unavailable';tag.textContent=tr('gpuSecureRequired');tag.title=tr('gpuSecureHint');refreshAiSetup();return}if(!navigator.gpu){gpuState='unavailable';tag.textContent=tr('gpuMissing');tag.title=tr('gpuUnsupportedHint');refreshAiSetup();return}try{const adapter=await navigator.gpu.requestAdapter();if(!adapter){gpuState='unavailable';tag.textContent=tr('gpuAdapterMissing');tag.title=tr('gpuAdapterHint');refreshAiSetup();return}gpuState='available';tag.textContent=tr('gpuAvailable');tag.classList.add('ready');const info=adapter.info||{};const dev=navigator.deviceMemory?` · ${tr('memoryEstimate')} ${navigator.deviceMemory} GB RAM`:` · ${tr('memoryUnknown')}`;tag.title=`${info.vendor||''} ${info.architecture||''}${dev} · ${tr('enginePending')}`;refreshAiSetup()}catch(e){gpuState='unavailable';tag.textContent=tr('gpuMissing');tag.title=e.message;refreshAiSetup()}}
function applyPrefs(){document.documentElement.style.setProperty('--font',`${prefs.font}px`);document.body.classList.toggle('light',prefs.theme==='light');$('#theme').value=prefs.theme;$('#board-material').value=prefs.board;$('#stone-material').value=prefs.stones;const activeSize=root?boardSize():prefs.size;if(!Array.from($('#board-size').options).some(o=>Number(o.value)===activeSize))$('#board-size').add(new Option(activeSize,activeSize));$('#board-size').value=String(activeSize);$('#font-size').value=prefs.font;$('#font-value').value=`${prefs.font} px`;$('#placement-sound').value=prefs.sound;$('#motion').value=prefs.motion;drawBoard();drawStonePreviews()}
function drawStonePreviews(){for(const [selector,color] of [['#stone-preview-black',BLACK],['#stone-preview-white',WHITE]]){const canvas=$(selector);if(!canvas)continue;const context=canvas.getContext('2d');context.clearRect(0,0,canvas.width,canvas.height);context.save();context.scale(canvas.width/96,canvas.height/72);paintStone(context,48,36,25,color);context.restore()}}
function openSettings(){const d=$('#settings-dialog');d.dataset.before=JSON.stringify(prefs);applyPrefs();d.showModal()}
function restoreSettings(){const before=$('#settings-dialog').dataset.before;if(before){prefs=JSON.parse(before);applyPrefs()}}
function showGameChooser(games){const dialog=$('#game-chooser');const select=$('#game-choice');select.innerHTML=games.map((g,i)=>`<option value="${i}">${i+1}. ${escapeHtml(g.props.GN?.[0]||g.props.PB?.[0]||'Game')} · ${countNodes(g)} nodes</option>`).join('');dialog.showModal();$('#choose-game').onclick=()=>{const index=Number(select.value);loadSgfTree(games[index],games)}}
function bind(){
 $('#language').onchange=e=>{language=e.target.value;localStorage.removeItem(LANGUAGE_COOKIE);saveLanguageCookie(language);applyLanguage();refresh()};$('#settings-open').onclick=openSettings;
 $('#new-game').onclick=()=>{if(dirty)saveLibrary(false);setupNew(Number(prefs.size))};$('#import-button').onclick=()=>$('#file-input').click();$('#file-input').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{if(dirty)saveLibrary(false);const bytes=await f.arrayBuffer();const header=new TextDecoder('ascii').decode(bytes.slice(0,8192));const charset=header.match(/\bCA\[([^\]]+)\]/)?.[1]||'ISO-8859-1';let contents;try{contents=new TextDecoder(charset).decode(bytes)}catch{contents=new TextDecoder('utf-8').decode(bytes)}const games=parseSgf(contents);loadSgfTree(games[0],games);if(games.length>1)showGameChooser(games)}catch(err){console.error(err);toast(tr('badSgf'))}e.target.value=''};
 $('#save-sgf').onclick=downloadSgf;$('#send-mail').onclick=openMailDialog;$('#mail-address').oninput=e=>{if(e.target.checkValidity()&&e.target.value.trim())localStorage.setItem('ng.mail-address',e.target.value.trim())};$('#open-mail').onclick=sendGameMail;$('#score-game').onclick=scoreGame;$('#undo').onclick=previous;$('#redo').onclick=()=>next(0);$('#previous').onclick=previous;$('#next').onclick=()=>next(0);$('#first').onclick=()=>navigateTo(root);$('#last').onclick=()=>{let n=root;while(n.children?.length)n=n.children[0];navigateTo(n)};$('#pass').onclick=()=>appendMove(0,0,true);$('#main-line').onclick=()=>{$('#main-line').classList.toggle('active');refreshTree()};$('#collapse-tree').onclick=()=>{treePan.x=0;treePan.y=0;$('#tree-scroll').scrollTo({left:0,top:0,behavior:'smooth'});refreshTree()};bindTreePan();$('#review-game').onclick=reviewGame;$('#check-gpu').onclick=checkGpu;$('#model-center').onclick=openModelCenter;$('#model-file').onchange=e=>importModel(e.target.files[0]).catch(err=>toast(err.message));$('#save-ai-config').onclick=downloadAiConfig;$('#export-ai-config').onclick=()=>{const config=storedAiConfig();if(!config)return;const blob=new Blob([JSON.stringify(config,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='nightygo-ai-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};$('#ai-config-file').onchange=e=>importAiConfig(e.target.files[0]).catch(err=>toast(err.message));$('#search-visits').onchange=refreshAiSetup;$('#search-time').onchange=refreshAiSetup;$('#load-model').onclick=()=>loadSelectedModel().catch(err=>toast(err.message));$('#analyze-position').onclick=analyzePosition;$('#play-ai').onclick=playAiMove;
 $('#markup-tool').onchange=e=>{pendingLinePoint=null;$('#markup-label').disabled=e.target.value!=='LB';drawBoard()};$('#markup-label').disabled=true;const canvas=$('#go-board');canvas.onpointermove=e=>{const p=boardPoint(e.clientX,e.clientY);pointer=p.distance<canvas.getBoundingClientRect().width*.055?{x:p.x,y:p.y}:null;drawBoard()};canvas.onpointerleave=()=>{pointer=null;drawBoard()};canvas.onpointerdown=e=>{if(e.button!==0)return;const p=boardPoint(e.clientX,e.clientY);if(p.distance>canvas.getBoundingClientRect().width*.055)return;if(addMarkup(p.x,p.y))return;try{const ko=last&&!last.pass&&positionHistory.length>1?positionHistory.at(-2):null;const result=applyMove(board,toPlay,p.x,p.y,true,ko);const cap=result.captured.length;appendMove(p.x,p.y);if(cap)playCapture(cap)}catch(err){toast(err.message||tr('illegal'))}};canvas.onkeydown=e=>{if(e.key==='ArrowLeft')previous();if(e.key==='ArrowRight')next(0)};window.addEventListener('resize',()=>{resizeCanvas();refreshTree()});new ResizeObserver(()=>{resizeCanvas();refreshTree()}).observe($('#board-wrap'));
 $('#save-comment').onclick=()=>{updateComment($('#comment').value);toast(tr('commentSaved'))};$('#edit-info').onclick=()=>{for(const [id,key] of [['edit-black','PB'],['edit-white','PW'],['edit-event','EV'],['edit-result','RE'],['edit-komi','KM']])$('#'+id).value=root.props[key]?.[0]||'';$('#info-dialog').showModal()};$('#apply-info').onclick=()=>{for(const [id,key] of [['edit-black','PB'],['edit-white','PW'],['edit-event','EV'],['edit-result','RE'],['edit-komi','KM']])setProp(key,$('#'+id).value.trim());const handicap=Math.max(0,Math.min(9,Number($('#edit-handicap').value)||0));if(path.length>1&&handicap!==Number(root.props.HA?.[0]||0)){toast('讓子只能在開始對局前設定');return}setProp('HA',handicap?String(handicap):'');if(path.length===1){if(handicap)root.props.AB=handicapPoints(boardSize(),handicap);else delete root.props.AB;if(handicap)root.props.PL=['W'];else delete root.props.PL;rebuild();refresh()}toast(tr('metadataSaved'))};$('#library-search').oninput=refreshLibrary;
 $('#font-size').oninput=e=>{$('#font-value').value=`${e.target.value} px`;document.documentElement.style.setProperty('--font',`${e.target.value}px`)};$('#preview-sound').onclick=()=>playSound($('#placement-sound').value);$('#theme').onchange=e=>document.body.classList.toggle('light',e.target.value==='light');$('#motion').onchange=e=>{prefs.motion=e.target.value;drawBoard()};$('#board-material').onchange=e=>{prefs.board=e.target.value;drawBoard()};$('#stone-material').onchange=e=>{prefs.stones=e.target.value;drawBoard();drawStonePreviews()};$('#save-settings').onclick=()=>{const newSize=Number($('#board-size').value);prefs={...prefs,theme:$('#theme').value,board:$('#board-material').value,stones:$('#stone-material').value,size:newSize,font:Number($('#font-size').value),sound:$('#placement-sound').value,motion:$('#motion').value};if(newSize!==boardSize()){prefs.size=newSize;setupNew(newSize);toast(tr('settingsApplied'))}else{writeStore('ng.preferences',prefs);applyPrefs();toast(tr('settingsApplied'))}};$('#settings-dialog').addEventListener('close',()=>{if($('#settings-dialog').returnValue!=='default')restoreSettings();else{prefs={...prefs,theme:$('#theme').value,board:$('#board-material').value,stones:$('#stone-material').value,font:Number($('#font-size').value),sound:$('#placement-sound').value,motion:$('#motion').value};writeStore('ng.preferences',prefs);applyPrefs()}});
 $('#install-app').onclick=async()=>{if(pendingInstall){pendingInstall.prompt();pendingInstall=null;$('#install-app').hidden=true}};window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();pendingInstall=e;$('#install-app').hidden=false});window.addEventListener('beforeunload',e=>{if(root&&dirty){writeStore('ng.autosave',serializeCollection());e.preventDefault();e.returnValue=''}});
}
function init(){applyLanguage();applyPrefs();drawStonePreviews();bind();const auto=localStorage.getItem('ng.autosave');if(auto){try{const trees=parseSgf(auto);collectionTrees=trees;const tree=trees[0];root=tree;current=root;path=[root];while(current.children?.length){current=current.children[0];path.push(current)}dirty=true}catch{setupNew()}}else setupNew();refresh();refreshModels().catch(error=>console.warn('Could not read local models',error));checkGpu();if('serviceWorker'in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('sw.js').catch(()=>{});}
init();
