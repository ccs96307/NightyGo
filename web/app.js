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
 'zh-Hant':{sendMail:'寄送郵件',mailIntro:'輸入收件者 Email，將在你的郵件 App 開啟草稿，棋譜會放在郵件內容中。',emailAddress:'收件者 Email',mailStorageNote:'此 Email 只儲存在這台裝置的 NightyGo 網站資料中；只清除快取通常不會刪除，清除網站資料才會移除。',openMail:'開啟郵件草稿',mailTooLarge:'棋譜太長，無法放入郵件草稿。請改用「匯出 SGF」後附加檔案。',mailSubject:'NightyGo 圍棋棋譜',mailBody:'你好，這是我分享的圍棋棋譜。SGF 內容如下：'},
 'zh-Hans':{sendMail:'发送邮件',mailIntro:'输入收件人 Email，将在你的邮件 App 中打开草稿，棋谱会放在邮件正文中。',emailAddress:'收件人 Email',mailStorageNote:'此 Email 仅保存在这台设备的 NightyGo 网站数据中；仅清除缓存通常不会删除，清除网站数据才会移除。',openMail:'打开邮件草稿',mailTooLarge:'棋谱太长，无法放入邮件草稿。请改用“导出 SGF”后添加附件。',mailSubject:'NightyGo 围棋棋谱',mailBody:'你好，这是我分享的围棋棋谱。SGF 内容如下：'},
 en:{sendMail:'Send Mail',mailIntro:'Enter a recipient email. Your mail app will open a draft with the game record in the message body.',emailAddress:'Recipient email',mailStorageNote:'This email is stored only in NightyGo site data on this device. Clearing cached files alone usually keeps it; clearing site data removes it.',openMail:'Open mail draft',mailTooLarge:'This game is too large to fit in a mail draft. Export the SGF and attach the file instead.',mailSubject:'NightyGo Go game record',mailBody:'Hello, here is the Go game record I am sharing. SGF follows:'},
 ja:{sendMail:'メールで送る',mailIntro:'宛先のメールアドレスを入力すると、棋譜を本文に含むメールの下書きをメールアプリで開きます。',emailAddress:'宛先メールアドレス',mailStorageNote:'メールアドレスはこの端末のNightyGoサイトデータにのみ保存されます。キャッシュのみを消去しても通常は残りますが、サイトデータを消去すると削除されます。',openMail:'メールの下書きを開く',mailTooLarge:'棋譜が長すぎてメールの下書きに入りません。「SGFを書き出す」を使ってファイルを添付してください。',mailSubject:'NightyGo 囲碁棋譜',mailBody:'こんにちは。共有する囲碁棋譜です。SGF：'},
 ko:{sendMail:'메일 보내기',mailIntro:'받는 사람 이메일을 입력하면 기보가 본문에 포함된 초안을 메일 앱에서 엽니다.',emailAddress:'받는 사람 이메일',mailStorageNote:'이 이메일은 이 기기의 NightyGo 사이트 데이터에만 저장됩니다. 캐시만 지우면 보통 유지되며 사이트 데이터를 지우면 삭제됩니다.',openMail:'메일 초안 열기',mailTooLarge:'기보가 너무 길어 메일 초안에 넣을 수 없습니다. SGF 내보내기를 사용해 파일을 첨부하세요.',mailSubject:'NightyGo 바둑 기보',mailBody:'안녕하세요. 공유할 바둑 기보입니다. SGF:'}
};
for(const [locale,values] of Object.entries(MAIL_I18N))Object.assign(I18N[locale],values);
const TOUCH_I18N={'zh-Hant':{touchPlaceHint:'點一下預覽棋子，再點一次落子'},'zh-Hans':{touchPlaceHint:'轻点预览棋子，再点一次落子'},en:{touchPlaceHint:'Tap once to preview a stone, then tap it again to place.'},ja:{touchPlaceHint:'1回タップして碁石をプレビューし、もう1回タップして着手します'},ko:{touchPlaceHint:'한 번 눌러 돌을 미리 보고, 같은 곳을 다시 눌러 착수하세요'}};
for(const [locale,values] of Object.entries(TOUCH_I18N))Object.assign(I18N[locale],values);
Object.assign(I18N['zh-Hans'],{browserReady:'浏览器就绪',currentGame:'当前棋局',unsaved:'未保存',blackCaptured:'黑方提子',move:'手数',whiteCaptured:'白方提子',navigation:'棋谱导航',gameTree:'棋谱树',mainLine:'主线',fitTree:'适配',branchOnVariation:'只在分支处分叉',black:'黑',white:'白',variations:'变化',engine:'引擎',aiStudio:'AI 研究室',browserAiTitle:'浏览器 AI 引擎',browserAiBody:'检查 WebGPU 与可用内存。AI 引擎尚未连接，因此不会显示虚构分析。',checkGpu:'检查 WebGPU',visits:'搜索次数',winrate:'胜率',scoreLead:'目差',engineNotBundled:'本次尚未集成可运行的 KataGo WebGPU/WASM 引擎，因此不提供虚假候选着。',review:'整盘复盘',notAvailable:'暂不可用',details:'棋局信息',gameInfo:'棋局信息',edit:'编辑',blackPlayer:'黑方',whitePlayer:'白方',event:'赛事',result:'结果',comment:'当前节点注释',saveComment:'保存注释',libraryLabel:'你的棋谱收藏',library:'棋谱库',saveSgf:'导出 SGF',localData:'棋局与偏好仅保存在此浏览器',installApp:'安装网页应用',settings:'设置',theme:'界面主题',dark:'深色',light:'浅色',boardMaterial:'棋盘材质',stoneMaterial:'棋子材质',boardSize:'棋盘尺寸',fontSize:'字体大小',placementSound:'落子音效',preview:'试听',motion:'动态背景',cancel:'取消',apply:'应用',editGameInfo:'编辑棋局信息',komi:'贴目'});
Object.assign(I18N.ja,{browserReady:'ブラウザー準備完了',workbench:'囲碁ワークベンチ',subtitle:'対局、棋譜の整理、新しい変化の研究。',currentGame:'現在の対局',unsaved:'未保存',blackTurn:'黒番',whiteTurn:'白番',blackCaptured:'黒のアゲハマ',whiteCaptured:'白のアゲハマ',move:'手数',undo:'戻す',redo:'やり直す',pass:'パス',navigation:'棋譜ナビゲーション',gameTree:'棋譜ツリー',mainLine:'本線',fitTree:'全体表示',branchOnVariation:'変化点のみ分岐',black:'黒',white:'白',variations:'変化',engine:'エンジン',aiStudio:'AIスタジオ',browserAiTitle:'ブラウザーAIエンジン',browserAiBody:'WebGPUとメモリーを確認します。AIエンジン未接続のため、架空の解析は表示しません。',checkGpu:'WebGPUを確認',visits:'探索数',winrate:'勝率',scoreLead:'目差',engineNotBundled:'KataGo WebGPU/WASMエンジンは未同梱です。候補手を捏造して表示しません。',review:'全局検討',notAvailable:'未対応',details:'対局情報',gameInfo:'対局情報',edit:'編集',blackPlayer:'黒番',whitePlayer:'白番',event:'大会',result:'結果',comment:'この局面のコメント',saveComment:'コメントを保存',libraryLabel:'棋譜コレクション',library:'棋譜ライブラリー',saveSgf:'SGFを書き出す',localData:'棋譜と設定はこのブラウザーに保存',installApp:'ウェブアプリをインストール',settings:'設定',theme:'画面テーマ',dark:'ダーク',light:'ライト',boardMaterial:'盤の素材',stoneMaterial:'碁石の素材',boardSize:'盤サイズ',fontSize:'文字サイズ',placementSound:'着手音',preview:'試聴',motion:'背景アニメーション',cancel:'キャンセル',apply:'適用',editGameInfo:'対局情報を編集',komi:'コミ'});
Object.assign(I18N.ko,{browserReady:'브라우저 준비 완료',workbench:'바둑 워크벤치',subtitle:'대국하고 기보를 정리하며 새로운 변화를 연구하세요.',currentGame:'현재 대국',unsaved:'저장되지 않음',blackTurn:'흑 차례',whiteTurn:'백 차례',blackCaptured:'흑 포획',whiteCaptured:'백 포획',move:'수',undo:'무르기',redo:'다시 실행',pass:'패스',navigation:'기보 탐색',gameTree:'기보 트리',mainLine:'주요 진행',fitTree:'맞춤',branchOnVariation:'변화점에서만 분기',black:'흑',white:'백',variations:'변화',engine:'엔진',aiStudio:'AI 스튜디오',browserAiTitle:'브라우저 AI 엔진',browserAiBody:'WebGPU와 메모리를 확인합니다. AI 엔진이 연결되지 않아 가짜 분석은 표시하지 않습니다.',checkGpu:'WebGPU 확인',visits:'탐색 횟수',winrate:'승률',scoreLead:'집 차이',engineNotBundled:'실행 가능한 KataGo WebGPU/WASM 엔진이 아직 포함되지 않아 후보 수를 표시하지 않습니다.',review:'전체 복기',notAvailable:'아직 사용할 수 없음',details:'대국 정보',gameInfo:'대국 정보',edit:'편집',blackPlayer:'흑',whitePlayer:'백',event:'대회',result:'결과',comment:'현재 노드 주석',saveComment:'주석 저장',libraryLabel:'내 기보 컬렉션',library:'기보 라이브러리',saveSgf:'SGF 내보내기',localData:'대국과 설정은 이 브라우저에 저장됩니다',installApp:'웹 앱 설치',settings:'설정',theme:'화면 테마',dark:'다크',light:'라이트',boardMaterial:'바둑판 재질',stoneMaterial:'바둑돌 재질',boardSize:'판 크기',fontSize:'글꼴 크기',placementSound:'착수 효과음',preview:'미리 듣기',motion:'배경 움직임',cancel:'취소',apply:'적용',editGameInfo:'대국 정보 편집',komi:'덤'});
Object.assign(I18N['zh-Hant'],{sound1:'木板落子 1',sound2:'木板落子 2',sound3:'木板落子 3',sound4:'木板落子 4',sound5:'木板落子 5',soundMeow:'貓叫',versus:' 對 ',browserTitle:'未命名棋局'});
Object.assign(I18N['zh-Hans'],{sound1:'木板落子 1',sound2:'木板落子 2',sound3:'木板落子 3',sound4:'木板落子 4',sound5:'木板落子 5',soundMeow:'猫叫',versus:' 对 ',browserTitle:'未命名棋局'});
Object.assign(I18N.en,{sound1:'Wooden board · 1',sound2:'Wooden board · 2',sound3:'Wooden board · 3',sound4:'Thin board · 1',sound5:'Thin board · 2',soundMeow:'Cat meow',versus:' vs ',browserTitle:'Untitled game'});
Object.assign(I18N.ja,{sound1:'木の碁盤 · 1',sound2:'木の碁盤 · 2',sound3:'木の碁盤 · 3',sound4:'薄い碁盤 · 1',sound5:'薄い碁盤 · 2',soundMeow:'猫の鳴き声',versus:' 対 ',browserTitle:'無題の対局'});
Object.assign(I18N.ko,{sound1:'나무 바둑판 · 1',sound2:'나무 바둑판 · 2',sound3:'나무 바둑판 · 3',sound4:'얇은 바둑판 · 1',sound5:'얇은 바둑판 · 2',soundMeow:'고양이 울음',versus:' 대 ',browserTitle:'제목 없는 대국'});
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
for(const [locale,values] of Object.entries({
 'zh-Hant':{modelWelcome:'在此瀏覽器執行 KataGo。模型只儲存在你的裝置，不會上傳。',downloadModelsHeading:'選擇適合的模型',modelAdvice:'依照裝置效能挑選模型，也可下載後自動加入本機模型庫。',lightModelHint:'載入較快 · 記憶體需求較低',balancedModelHint:'強度與速度兼顧',strongModelHint:'分析能力最強 · 需要較多記憶體',modelSetupHeading:'模型與搜尋設定',modelSetupHint:'匯入模型檔，或選擇已儲存在此瀏覽器的模型。'},
 'zh-Hans':{modelWelcome:'在此浏览器运行 KataGo。模型只保存在你的设备，不会上传。',downloadModelsHeading:'选择适合的模型',modelAdvice:'根据设备性能选择模型，也可下载后自动加入本地模型库。',lightModelHint:'加载更快 · 内存需求较低',balancedModelHint:'兼顾棋力与速度',strongModelHint:'分析能力最强 · 需要更多内存',modelSetupHeading:'模型与搜索设置',modelSetupHint:'导入模型文件，或选择已保存在此浏览器的模型。'},
 en:{modelWelcome:'Run KataGo in this browser. Models stay on your device and are never uploaded.',downloadModelsHeading:'Choose your model',modelAdvice:'Pick a model for your device. Downloads are added to your local model library.',lightModelHint:'Quicker setup · lower memory use',balancedModelHint:'A balance of strength and speed',strongModelHint:'Strongest analysis · needs more memory',modelSetupHeading:'Model and search settings',modelSetupHint:'Import a model file or select one already stored in this browser.'},
 ja:{modelWelcome:'このブラウザーでKataGoを実行します。モデルは端末内に保存され、アップロードされません。',downloadModelsHeading:'モデルを選択',modelAdvice:'端末の性能に合ったモデルを選択してください。ダウンロードしたモデルは自動で保存されます。',lightModelHint:'読み込みが速い · メモリー使用量が少ない',balancedModelHint:'棋力と速度のバランス',strongModelHint:'最も強力 · 多くのメモリーが必要',modelSetupHeading:'モデルと探索設定',modelSetupHint:'モデルを読み込むか、このブラウザーに保存済みのモデルを選択します。'},
 ko:{modelWelcome:'이 브라우저에서 KataGo를 실행합니다. 모델은 기기에 저장되며 업로드되지 않습니다.',downloadModelsHeading:'모델 선택',modelAdvice:'기기 성능에 맞는 모델을 선택하세요. 다운로드한 모델은 자동으로 저장됩니다.',lightModelHint:'빠른 설정 · 적은 메모리 사용',balancedModelHint:'기력과 속도의 균형',strongModelHint:'가장 강한 분석 · 더 많은 메모리 필요',modelSetupHeading:'모델 및 탐색 설정',modelSetupHint:'모델 파일을 가져오거나 이 브라우저에 저장된 모델을 선택하세요.'}
}))Object.assign(I18N[locale],values);
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
for (const [locale, values] of Object.entries({
  'zh-Hant': {mimiMode:'Mimi 模式', mimiBoard:'Mimi 奶油爪印', mimiStones:'Mimi 黑白貓'},
  'zh-Hans': {mimiMode:'Mimi 模式', mimiBoard:'Mimi 奶油爪印', mimiStones:'Mimi 黑白猫'},
  en: {mimiMode:'Mimi Mode', mimiBoard:'Mimi · Cream & Paws', mimiStones:'Mimi · Cat Stones'},
  ja: {mimiMode:'Mimiモード', mimiBoard:'Mimi · クリームと肉球', mimiStones:'Mimi · 黒猫と白猫'},
  ko: {mimiMode:'Mimi 모드', mimiBoard:'Mimi · 크림과 발바닥', mimiStones:'Mimi · 검은 고양이와 흰 고양이'}
})) Object.assign(I18N[locale], values);
for (const [locale, values] of Object.entries({
  'zh-Hant': {ruleMapToggle:'規則估算', aiMapToggle:'AI 領地', boardOverlayRule:'面積估算（不含死活判定）：黑 {black} · 白 {white}（含貼目）', boardOverlayAi:'AI 預測領地', overlayHidden:'已關閉棋盤判斷圖層'},
  'zh-Hans': {ruleMapToggle:'规则估算', aiMapToggle:'AI 领地', boardOverlayRule:'面积估算（不含死活判定）：黑 {black} · 白 {white}（含贴目）', boardOverlayAi:'AI 预测领地', overlayHidden:'已关闭棋盘判断图层'},
  en: {ruleMapToggle:'Rule map', aiMapToggle:'AI map', boardOverlayRule:'Area estimate · Black {black} · White {white}, komi included · Life and death not judged', boardOverlayAi:'AI predicted ownership', overlayHidden:'Board overlays hidden'},
  ja: {ruleMapToggle:'ルール推定', aiMapToggle:'AI領地', boardOverlayRule:'面積推定（死活判定なし）：黒 {black} · 白 {white}（コミ込み）', boardOverlayAi:'AI予測の領地', overlayHidden:'盤面の判定表示を閉じました'},
  ko: {ruleMapToggle:'규칙 추정', aiMapToggle:'AI 영역', boardOverlayRule:'면적 추정(사활 판정 없음): 흑 {black} · 백 {white}(덤 포함)', boardOverlayAi:'AI 예상 영역', overlayHidden:'바둑판 판정 레이어를 닫았습니다'}
})) Object.assign(I18N[locale], values);
let language = initialLanguage();
const savedPrefs = readStore('ng.preferences', null);
let prefs = Object.assign({board:savedPrefs?'wood':'night',stones:savedPrefs?'classic':'moon',size:19,font:17,sound:'01',motion:'full',theme:'dark'}, savedPrefs || {});
if (savedPrefs?.font === 15) prefs.font = 17;
let pendingLinePoint=null;
let collectionTrees=[], root, current, board = [], captures = {[BLACK]:0,[WHITE]:0}, toPlay = BLACK, last = null, path = [], positionHistory=[], dirty=false, pointer=null, touchPreviewAnchor=null, animationFrame=0, library=readStore('ng.library',[]), pendingInstall, engineWorker=null, activeModelId='', engineBoardSize=0, engineReady=false, analyzedNode=null, analyzedBoard=null, ownershipMap=null, engineRequestId=0;
let ruleOwnershipMap=null,ruleEstimate=null,ruleEstimateBoard=null,ruleEstimateNode=null,showRuleEstimate=false,showAiOwnership=false;
let animationTimer = 0, gpuState = 'unknown', gpuReason = 'checking', gpuError = '', modelAvailable = false;
let modelBackendGpu=false,modelVersion=null,lastAnalysisScore=0,analysisOutputType='position',reviewResults=[],reviewMoveCount=0,reviewLine=[],aiProgressState=null,modelLoadingStage='initializingEngine',candidateAnalysis=[];
const skyStartedAt = performance.now() / 1000;
const treePan = {x:0, y:0, width:320, height:240, root:null, dragging:false, moved:false, lastX:0, lastY:0};
const modelDb = () => new Promise((resolve,reject)=>{const req=indexedDB.open('nightygo-models-v1',1);req.onupgradeneeded=()=>req.result.createObjectStore('models',{keyPath:'id'});req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)});
async function putModel(model){const db=await modelDb();return new Promise((resolve,reject)=>{const tx=db.transaction('models','readwrite');tx.objectStore('models').put(model);tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error)})}
async function getModel(id){const db=await modelDb();return new Promise((resolve,reject)=>{const req=db.transaction('models').objectStore('models').get(id);req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
async function listModels(){const db=await modelDb();return new Promise((resolve,reject)=>{const models=[],req=db.transaction('models').objectStore('models').openCursor();req.onsuccess=()=>{const cursor=req.result;if(!cursor){resolve(models);return}const {id,name,size,added}=cursor.value;models.push({id,name,size,added});cursor.continue()};req.onerror=()=>reject(req.error)})}
function engineRequest(type,payload={}){return new Promise((resolve,reject)=>{if(!engineWorker)engineWorker=new Worker(new URL('./engine-worker.js',import.meta.url));const worker=engineWorker,requestId=++engineRequestId;const cleanup=()=>{worker.removeEventListener('message',onMessage);worker.removeEventListener('error',onError);worker.removeEventListener('messageerror',onMessageError)};const onMessage=event=>{if(event.data.requestId!==requestId)return;if(event.data.type==='progress'){setModelLoadingStatus(event.data.stage);return}if(event.data.type==='analysisProgress'){setAiProgress('candidateSearchProgress',{current:event.data.current,total:event.data.total,move:candidateName(event.data.loc)});return}if(event.data.type==='analysisCandidate'){candidateAnalysis=candidateAnalysis.map(candidate=>candidate.loc===event.data.candidate.loc?event.data.candidate:candidate).sort((a,b)=>(b.winrate??-1)-(a.winrate??-1));updateCandidateVisitSummary();renderCandidates();drawBoard();return}cleanup();if(event.data.type==='error')reject(Error(event.data.message));else resolve(event.data.result)};const onError=event=>{cleanup();reject(Error(event.message||'KataGo worker failed to start'))};const onMessageError=()=>{cleanup();reject(Error('Could not read the KataGo worker response'))};worker.addEventListener('message',onMessage);worker.addEventListener('error',onError);worker.addEventListener('messageerror',onMessageError);try{worker.postMessage({type,requestId,...payload},payload.bytes?[payload.bytes]:[])}catch(error){cleanup();reject(error)}})}
function movesForPath(nodes=path){const rootProps=nodes[0]?.props||{};if(rootProps.AW||rootProps.AE||nodes.slice(1).some(n=>n.props?.AB||n.props?.AW||n.props?.AE))throw Error(tr('unsupportedSetup'));const setup=expandSetup(rootProps.AB,boardSize());if(setup.length===1)throw Error(tr('unsupportedHandicap'));return [...setup.map(([x,y])=>({loc:y*boardSize()+x,color:BLACK})),...nodes.flatMap(node=>{const p=node.props||{};const color=p.B?BLACK:p.W?WHITE:null;if(!color)return[];const value=(p.B||p.W)[0];return [{loc:value===''?-1:(value.charCodeAt(1)-97)*boardSize()+value.charCodeAt(0)-97,color}]})]}
async function refreshModels(){const models=await listModels();modelAvailable=models.length>0;const select=$('#model-select');select.innerHTML=models.length?models.map(m=>`<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)} · ${(m.size/1048576).toFixed(1)} MB</option>`).join(''):`<option value="">${tr('noModel')}</option>`;const remembered=localStorage.getItem('ng.last-model-id');if(activeModelId&&models.some(m=>m.id===activeModelId))select.value=activeModelId;else if(remembered&&models.some(m=>m.id===remembered))select.value=remembered;else if(models.length)select.value=models[0].id;const memory=navigator.deviceMemory||4;const tier=memory<4?0:memory<8?1:2;const advice={'zh-Hant':`裝置記憶體粗估 ${memory} GB，建議${['輕量','平衡','高強度'][tier]}模型。此數字僅為瀏覽器估值；棋盤尺寸與可用 GPU 記憶體也會影響載入。模型只存在本機瀏覽器。`,'zh-Hans':`设备内存粗估 ${memory} GB，建议${['轻量','均衡','高强度'][tier]}模型。该数字仅为浏览器估值；棋盘大小和 GPU 可用内存也会影响加载。模型只保存在本地浏览器。`,en:`Estimated device memory: ${memory} GB. Suggested tier: ${['light','balanced','strong'][tier]}. This browser estimate is approximate; board size and GPU memory also affect model loading. Models stay in this browser.`,ja:`端末メモリーの推定は ${memory} GB。おすすめ：${['軽量','標準','高性能'][tier]}モデル。ブラウザーによる概算で、盤サイズとGPUメモリーも読み込みに影響します。モデルはこのブラウザーに保存されます。`,ko:`기기 메모리 추정치 ${memory} GB. 추천 모델: ${['경량','균형','고성능'][tier]}. 브라우저 추정값이며 바둑판 크기와 GPU 메모리도 로딩에 영향을 줍니다. 모델은 이 브라우저에 저장됩니다.`};$('#model-advice').textContent=advice[language]||advice.en;refreshAiSetup();return models}
function storedAiConfig(){try{const value=localStorage.getItem('ng.ai-profile');return value?validateAiConfig(JSON.parse(value)):null}catch{return null}}
function refreshAiSetup(){const config=storedAiConfig();const modelReady=modelAvailable||Boolean(activeModelId);$('#ai-model-status').textContent=modelReady?tr('setupReady'):tr('setupMissing');$('#ai-profile-status').textContent=config?tr('setupReady'):tr('setupMissing');$('#ai-model-status').className=modelReady?'is-ready':'is-missing';$('#ai-profile-status').className=config?'is-ready':'is-missing';$('#ai-setup-message').textContent=gpuState==='available'&&!config?tr('gpuReadySetupPrompt'):gpuState==='available'&&!modelReady?tr('gpuReadyModelPrompt'):gpuState==='available'?tr('gpuReadyComplete'):tr('gpuBeforeSetup');$('#ai-config-status').textContent=config?tr('profileReady'):tr('profileMissing');$('#export-ai-config').disabled=!config;if(config){$('#search-visits').value=String(config.searchVisits);$('#search-time').value=String(config.maxSearchTimeMs)}}
function saveAiConfig(config){const valid=validateAiConfig(config);localStorage.setItem('ng.ai-profile',JSON.stringify(valid));refreshAiSetup();return valid}
function downloadAiConfig(){const config=saveAiConfig({format:DEFAULT_AI_CONFIG.format,version:DEFAULT_AI_CONFIG.version,searchVisits:Number($('#search-visits').value),maxSearchTimeMs:Number($('#search-time').value)});const blob=new Blob([JSON.stringify(config,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='nightygo-ai-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
async function importAiConfig(file){if(!file)return;let config;try{config=parseAiConfig(await file.text())}catch(error){const key=({'AI profile is not valid JSON.':'profileJsonInvalid','AI profile must be a JSON object.':'profileObjectInvalid','Unsupported AI profile format or version.':'profileVersionInvalid','searchVisits must be 32, 128, or 512.':'profileVisitsInvalid','maxSearchTimeMs must be 5000, 15000, or 30000.':'profileTimeInvalid'})[error.message]||'profileImportFailed';throw Error(tr(key))}saveAiConfig(config);toast(tr('profileImported'))}
async function openModelCenter(){await refreshModels();$('#model-dialog').showModal()}
async function importModel(file){if(!file)return;if(!file.name.endsWith('.bin.gz'))throw Error(tr('modelImportExtension'));const bytes=await file.arrayBuffer();if(bytes.byteLength<1024||new Uint8Array(bytes,0,2)[0]!==31||new Uint8Array(bytes,0,2)[1]!==139)throw Error(tr('invalidModelFile'));const id=crypto.randomUUID?.()||`${Date.now()}-${Math.random()}`;await putModel({id,name:file.name,size:bytes.byteLength,bytes,added:Date.now()});activeModelId=id;localStorage.setItem('ng.last-model-id',id);await refreshModels();toast(tr('modelSavedLocal'))}
async function downloadOfficialModel(url,name){
  const dialog=$('#model-loading-dialog'),title=$('#model-loading-title'),status=$('#model-loading-status'),progress=$('.indeterminate-progress');
  title.textContent=tr('downloadingModel');status.textContent=tr('downloadStarting');progress.classList.remove('is-determinate');progress.removeAttribute('value');progress.removeAttribute('max');dialog.showModal();
  try{
    const response=await fetch(url);if(!response.ok)throw Error(`HTTP ${response.status}`);
    const total=Number(response.headers.get('content-length'))||0,reader=response.body?.getReader();let bytes;
    if(reader&&total){
      bytes=new Uint8Array(total);let loaded=0;progress.max=total;progress.classList.add('is-determinate');
      while(true){const {done,value}=await reader.read();if(done)break;if(loaded+value.length>total)throw Error(tr('modelDownloadLengthMismatch'));bytes.set(value,loaded);loaded+=value.length;progress.value=loaded;status.textContent=tr('downloadProgress',{loaded:(loaded/1048576).toFixed(0),total:(total/1048576).toFixed(0)})}
      if(loaded!==total)bytes=bytes.slice(0,loaded);
    }else if(reader){
      const chunks=[];let loaded=0;while(true){const {done,value}=await reader.read();if(done)break;chunks.push(value);loaded+=value.length;status.textContent=tr('downloadedSize',{loaded:(loaded/1048576).toFixed(0)})}bytes=new Uint8Array(loaded);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length}
    }else bytes=new Uint8Array(await response.arrayBuffer());
    if(bytes.byteLength<1024||bytes[0]!==31||bytes[1]!==139)throw Error(tr('invalidModelFile'));
    const storage=await navigator.storage?.estimate?.();if(storage?.quota&&storage.quota-storage.usage<bytes.byteLength*1.05)throw Error(tr('modelStorageInsufficient'));
    title.textContent=tr('savingModel');status.textContent=tr('savingModelLocally');
    const id=crypto.randomUUID?.()||`${Date.now()}-${Math.random()}`;await putModel({id,name,size:bytes.byteLength,bytes:bytes.buffer,added:Date.now()});bytes=null;
    localStorage.setItem('ng.last-model-id',id);if(!storedAiConfig())saveAiConfig(DEFAULT_AI_CONFIG);activeModelId=id;await refreshModels();
    title.textContent=tr('loadingModel');status.textContent=tr('initializingEngine');if($('#model-dialog').open)$('#model-dialog').close();
    const model=await getModel(id);if(engineWorker)engineWorker.terminate();engineWorker=null;engineReady=false;
    const loaded=await engineRequest('load',{bytes:model.bytes,size:boardSize()});engineReady=true;engineBoardSize=boardSize();modelBackendGpu=loaded.gpu;modelVersion=loaded.version;
    $('#analyze-position').disabled=false;$('#play-ai').disabled=false;$('#review-game').disabled=false;refreshGpuLanguage();$('#engine-message').textContent=tr(loaded.gpu?'modelLoadedGpu':'modelLoadedCpu',{version:loaded.version});refreshAiSetup();toast(tr('modelInstalled'));
  }catch(error){toast(error.message.includes('Failed to fetch')?tr('downloadCorsError'):error.message);throw error}
  finally{dialog.close();title.textContent=tr('loadingModel');status.textContent=tr('initializingEngine');progress.classList.remove('is-determinate');progress.removeAttribute('value');progress.removeAttribute('max')}
}
async function loadSelectedModel({automatic=false,id=$('#model-select').value}={}){if(!id)throw Error(tr('needModel'));if(!automatic&&!storedAiConfig())throw Error(tr('needProfile'));if(automatic&&!storedAiConfig())saveAiConfig(DEFAULT_AI_CONFIG);const model=await getModel(id);if(!model)throw Error(tr('modelNotFound'));if(engineWorker)engineWorker.terminate();engineWorker=null;engineReady=false;$('#analyze-position').disabled=true;$('#play-ai').disabled=true;$('#review-game').disabled=true;const dialog=$('#model-loading-dialog');setModelLoadingStatus('initializingEngine');dialog.classList.toggle('background-load',automatic);if(automatic)dialog.show();else dialog.showModal();try{const loaded=await engineRequest('load',{bytes:model.bytes,size:boardSize()});activeModelId=id;localStorage.setItem('ng.last-model-id',id);engineBoardSize=boardSize();engineReady=true;modelBackendGpu=loaded.gpu;modelVersion=loaded.version;analyzedNode=null;analyzedBoard=null;ownershipMap=null;showAiOwnership=false;updateOverlayToggles();refreshGpuLanguage();$('#engine-message').textContent=tr(loaded.gpu?'modelLoadedGpu':'modelLoadedCpu',{version:loaded.version});$('#analyze-position').disabled=false;$('#play-ai').disabled=false;$('#review-game').disabled=false;refreshAiSetup();$('#model-dialog').close();if(!automatic)toast(tr('modelLoaded'))}finally{dialog.close();dialog.classList.remove('background-load')}}
function legalCandidates(candidates){return candidates.filter(c=>{if(c.loc===boardSize()*boardSize())return true;const x=c.loc%boardSize(),y=Math.floor(c.loc/boardSize());if(board[y]?.[x])return false;try{const ko=last&&!last.pass&&positionHistory.length>1?positionHistory.at(-2):null;applyMove(board,toPlay,x,y,true,ko);return true}catch{return false}}).slice(0,8)}
function candidateName(loc){return loc===boardSize()*boardSize()?tr('pass'):`${'ABCDEFGHJKLMNOPQRST'[loc%boardSize()]}${boardSize()-(loc/boardSize()|0)}`}
function updateCandidateVisitSummary(){const completed=candidateAnalysis.filter(candidate=>candidate.winrate!==null);const visits=completed.reduce((sum,candidate)=>sum+candidate.visits,0);$('#visits').textContent=completed.length?tr('candidateSearchSummary',{candidates:completed.length,visits}):candidateAnalysis.length?`0 / ${candidateAnalysis.length}`:tr('neuralInference')}
function renderCandidates(){const list=$('#candidate-list');list.innerHTML=candidateAnalysis.map((candidate,index)=>`<li class="candidate-row"><span class="candidate-rank">${index+1}</span><b class="candidate-coordinate">${candidateName(candidate.loc)}</b><span class="candidate-search-visits">${candidate.visits?tr('candidateVisits',{visits:candidate.visits}):'—'}</span><span class="candidate-winrate">${candidate.winrate===null?tr('searching'):`${(candidate.winrate*100).toFixed(1)}%`}</span></li>`).join('')}
async function analyzePosition(){
  const target=current,targetBoard=board,targetPlayer=toPlay,targetKomi=Number(root.props.KM?.[0]||7.5),button=$('#analyze-position');button.disabled=true;setAiProgress('analysisRunning');
  try{
    const moves=movesForPath(),initial=await engineRequest('analyze',{moves,toPlay:targetPlayer,komi:targetKomi});
    const top=legalCandidates(initial.candidates),config=storedAiConfig()||DEFAULT_AI_CONFIG;
    if(current!==target||board!==targetBoard||toPlay!==targetPlayer||Number(root.props.KM?.[0]||7.5)!==targetKomi)return;
    analyzedNode=target;analyzedBoard=targetBoard;analysisOutputType='position';lastAnalysisScore=initial.value[4];ownershipMap=initial.ownership;showAiOwnership=!!ownershipMap?.length;updateOverlayToggles();
    candidateAnalysis=top.map(candidate=>({loc:candidate.loc,score:candidate.score,winrate:null,visits:0}));drawBoard();$('#ai-empty').hidden=true;$('#analysis-results').hidden=false;
    updateCandidateVisitSummary();const win=initial.value[toPlay===WHITE?0:1];$('#winrate').textContent=`${(win*100).toFixed(1)}%`;
    $('#score-lead').textContent=tr('scoreLeadWhite',{score:`${initial.value[4]>=0?'+':''}${initial.value[4].toFixed(1)}`});renderCandidates();
    if(!top.length)return;
    const result=await engineRequest('analyzeCandidates',{moves,toPlay:targetPlayer,komi:targetKomi,candidateLocs:top.map(candidate=>candidate.loc),visits:config.searchVisits,maxSearchTimeMs:config.maxSearchTimeMs});
    if(current!==target||board!==targetBoard||toPlay!==targetPlayer||Number(root.props.KM?.[0]||7.5)!==targetKomi)return;
    candidateAnalysis=result.candidates;updateCandidateVisitSummary();renderCandidates();drawBoard();
  }catch(error){toast(error.message)}finally{button.disabled=!engineReady;hideAiProgress()}
}
async function playAiMove(){const target=current,targetBoard=board,targetPlayer=toPlay,targetKomi=Number(root.props.KM?.[0]||7.5),button=$('#play-ai');button.disabled=true;setAiProgress('searchRunning');try{const config=storedAiConfig();if(!config)throw Error(tr('needProfile'));const result=await engineRequest('search',{moves:movesForPath(),toPlay:targetPlayer,komi:targetKomi,visits:config.searchVisits,maxSearchTimeMs:config.maxSearchTimeMs});if(current!==target||board!==targetBoard||toPlay!==targetPlayer||Number(root.props.KM?.[0]||7.5)!==targetKomi)return;const loc=result.best;if(loc<0)appendMove(0,0,true);else appendMove(loc%boardSize(),Math.floor(loc/boardSize()));toast(tr('aiSearchSummary',{visits:result.visits,winrate:Math.round(result.winrate*100)}))}catch(error){toast(error.message)}finally{button.disabled=!engineReady;hideAiProgress()}}
async function reviewGame(){if(!engineWorker){toast(tr('loadModelFirst'));return}const line=[root];while(line.at(-1).children?.length)line.push(line.at(-1).children[0]);if(line.length>251){toast(tr('reviewLimit'));return}const button=$('#review-game');button.disabled=true;setAiProgress('reviewProgress',{current:0,total:line.length-1});const findings=[];try{for(let i=0;i<line.length;i++){const nodes=line.slice(0,i+1),moves=movesForPath(nodes),side=nodes.slice(1).reduce((p,node)=>node.props.B?WHITE:node.props.W?BLACK:p,nodes[0].props.PL?.[0]==='W'?WHITE:BLACK);const value=await engineRequest('analyze',{moves,toPlay:side,komi:Number(root.props.KM?.[0]||7.5)});findings.push({move:i,wr:value.value[0]});if(i%3===0||i===line.length-1)setAiProgress('reviewProgress',{current:i,total:line.length-1})}reviewResults=findings.slice(1).map((x,i)=>({...x,swing:Math.abs(x.wr-findings[i].wr)})).filter(x=>x.swing>.12).sort((a,b)=>b.swing-a.swing).slice(0,8);reviewMoveCount=findings.length-1;reviewLine=line;analysisOutputType='review';ownershipMap=null;showAiOwnership=false;updateOverlayToggles();$('#analysis-results').hidden=false;$('#ai-empty').hidden=true;renderReviewResults();$('#engine-message').textContent=tr('reviewComplete',{moves:reviewMoveCount})}catch(error){toast(error.message)}finally{button.disabled=!engineReady;hideAiProgress()}}
const AI_UI_I18N={
  'zh-Hant':{analyzePosition:'分析局面',playAiMove:'AI 落子',movePanel:'拖曳移動面板',loadingModel:'正在載入模型',loadingModelHint:'大型模型需要一些時間初始化。請保持此頁面開啟。',initializingEngine:'正在初始化推論引擎…',loadingNetwork:'正在載入神經網路…',modelLoaded:'KataGo 模型已載入',modelLoadedGpu:'KataGo v{version} 已載入。推論在本機執行；使用 WebGPU。',modelLoadedCpu:'KataGo v{version} 已載入。此裝置使用 CPU，分析可能較慢。',modelImportExtension:'請選擇 KataGo .bin.gz 網路檔',invalidModelFile:'這不是有效的 gzip 模型檔',modelSavedLocal:'模型已儲存於本機瀏覽器',neuralInference:'神經網路推論',scoreLeadWhite:'{score} 白方目差',aiSearchSummary:'AI 搜尋 {visits} 次 · {winrate}%',loadModelFirst:'請先載入 KataGo 模型',reviewLimit:'整盤覆盤目前最多處理 250 手',reviewProgress:'整盤覆盤中：{current}/{total}',reviewNoSwing:'主線各手勝率已計算，未發現大於 12% 的變化。',reviewComplete:'完成 {moves} 手主線覆盤；點擊列表可跳到變化較大的手。',unsupportedSetup:'AI 暫不支援棋盤編輯或白子初始設定；一般對局和標準黑棋讓子可分析。',unsupportedHandicap:'AI 僅支援標準兩子以上讓子設定。',boardSizeChanged:'棋盤尺寸已變更，請重新載入模型。',positionChanged:'局面已變更，請重新分析。'},
  'zh-Hans':{analyzePosition:'分析局面',playAiMove:'AI 落子',movePanel:'拖动以移动面板',loadingModel:'正在加载模型',loadingModelHint:'大型模型初始化需要一些时间。请保持此页面开启。',initializingEngine:'正在初始化推理引擎…',loadingNetwork:'正在加载神经网络…',modelLoaded:'KataGo 模型已加载',modelLoadedGpu:'KataGo v{version} 已加载。推理在本地运行；使用 WebGPU。',modelLoadedCpu:'KataGo v{version} 已加载。此设备使用 CPU，分析可能较慢。',modelImportExtension:'请选择 KataGo .bin.gz 网络文件',invalidModelFile:'这不是有效的 gzip 模型文件',modelSavedLocal:'模型已保存到本地浏览器',neuralInference:'神经网络推理',scoreLeadWhite:'{score} 白方目差',aiSearchSummary:'AI 搜索 {visits} 次 · {winrate}%',loadModelFirst:'请先加载 KataGo 模型',reviewLimit:'整盘复盘目前最多处理 250 手',reviewProgress:'整盘复盘中：{current}/{total}',reviewNoSwing:'主线各手胜率已计算，未发现大于 12% 的变化。',reviewComplete:'已完成 {moves} 手主线复盘；点击列表可跳到变化较大的手。',unsupportedSetup:'AI 暂不支持棋盘编辑或白棋初始设置；一般对局和标准黑棋让子可以分析。',unsupportedHandicap:'AI 仅支持标准两子以上让子设置。',boardSizeChanged:'棋盘大小已更改，请重新加载模型。',positionChanged:'局面已更改，请重新分析。'},
  en:{analyzePosition:'Analyze position',playAiMove:'AI move',movePanel:'Drag to move panel',loadingModel:'Loading model',loadingModelHint:'Large models can take a while to initialize. Keep this page open.',initializingEngine:'Initializing inference engine…',loadingNetwork:'Loading neural network…',modelLoaded:'KataGo model loaded',modelLoadedGpu:'KataGo v{version} loaded. Inference runs locally with WebGPU.',modelLoadedCpu:'KataGo v{version} loaded. This device is using the CPU, so analysis may be slower.',modelImportExtension:'Choose a KataGo .bin.gz network file',invalidModelFile:'This is not a valid gzip model file',modelSavedLocal:'Model saved in this browser',neuralInference:'Neural network inference',scoreLeadWhite:'{score} White lead',aiSearchSummary:'AI searched {visits} times · {winrate}%',loadModelFirst:'Load a KataGo model first',reviewLimit:'Full-game review currently supports up to 250 moves',reviewProgress:'Reviewing full game: {current}/{total}',reviewNoSwing:'Win rates are ready for the main line. No change greater than 12% was found.',reviewComplete:'Reviewed {moves} main-line moves. Select a result to jump to that position.',unsupportedSetup:'AI review does not support board edits or initial white stones yet. Standard games and standard black handicaps are supported.',unsupportedHandicap:'AI review supports standard handicaps of two or more stones.',boardSizeChanged:'Board size changed. Reload the model to continue.',positionChanged:'Position changed. Analyze again to refresh the results.'},
  ja:{analyzePosition:'局面を解析',playAiMove:'AIの着手',movePanel:'ドラッグしてパネルを移動',loadingModel:'モデルを読み込み中',loadingModelHint:'大きなモデルの初期化には時間がかかります。このページを開いたままお待ちください。',initializingEngine:'推論エンジンを初期化中…',loadingNetwork:'ニューラルネットワークを読み込み中…',modelLoaded:'KataGoモデルを読み込みました',modelLoadedGpu:'KataGo v{version}を読み込みました。WebGPUでローカル推論します。',modelLoadedCpu:'KataGo v{version}を読み込みました。CPUを使用するため解析に時間がかかる場合があります。',modelImportExtension:'KataGoの.bin.gzネットワークファイルを選択してください',invalidModelFile:'有効なgzipモデルファイルではありません',modelSavedLocal:'モデルをこのブラウザーに保存しました',neuralInference:'ニューラルネットワーク推論',scoreLeadWhite:'白の目差 {score}',aiSearchSummary:'AI探索 {visits}回 · {winrate}%',loadModelFirst:'先にKataGoモデルを読み込んでください',reviewLimit:'全局レビューは現在250手まで対応しています',reviewProgress:'全局レビュー中：{current}/{total}',reviewNoSwing:'主変化の勝率を計算しました。12%を超える変動はありません。',reviewComplete:'主変化の{moves}手をレビューしました。項目を選ぶと該当局面に移動します。',unsupportedSetup:'盤面編集や白石の初期配置は未対応です。通常の対局と標準的な黒の置き石は解析できます。',unsupportedHandicap:'標準的な2子以上の置き石に対応しています。',boardSizeChanged:'盤サイズが変わりました。モデルを再読み込みしてください。',positionChanged:'局面が変わりました。もう一度解析してください。'},
  ko:{analyzePosition:'국면 분석',playAiMove:'AI 착수',movePanel:'드래그하여 패널 이동',loadingModel:'모델 로딩 중',loadingModelHint:'대형 모델은 초기화에 시간이 걸릴 수 있습니다. 이 페이지를 열어 두세요.',initializingEngine:'추론 엔진 초기화 중…',loadingNetwork:'신경망 로딩 중…',modelLoaded:'KataGo 모델을 불러왔습니다',modelLoadedGpu:'KataGo v{version}을 불러왔습니다. WebGPU로 로컬 추론합니다.',modelLoadedCpu:'KataGo v{version}을 불러왔습니다. CPU를 사용하므로 분석이 느릴 수 있습니다.',modelImportExtension:'KataGo .bin.gz 네트워크 파일을 선택하세요',invalidModelFile:'올바른 gzip 모델 파일이 아닙니다',modelSavedLocal:'모델을 이 브라우저에 저장했습니다',neuralInference:'신경망 추론',scoreLeadWhite:'백 집 차 {score}',aiSearchSummary:'AI 탐색 {visits}회 · {winrate}%',loadModelFirst:'먼저 KataGo 모델을 불러오세요',reviewLimit:'전체 복기는 현재 최대 250수까지 지원합니다',reviewProgress:'전체 복기 중: {current}/{total}',reviewNoSwing:'주요 변화를 모두 계산했습니다. 12%를 넘는 변화가 없습니다.',reviewComplete:'주요 변화 {moves}수를 복기했습니다. 항목을 선택하면 해당 국면으로 이동합니다.',unsupportedSetup:'바둑판 편집과 백돌 초기 배치는 아직 지원하지 않습니다. 일반 대국과 표준 흑 돌가리기는 분석할 수 있습니다.',unsupportedHandicap:'표준 두 점 이상 접바둑을 지원합니다.',boardSizeChanged:'바둑판 크기가 바뀌었습니다. 모델을 다시 불러오세요.',positionChanged:'국면이 바뀌었습니다. 다시 분석하세요.'}
};
for(const [locale,values] of Object.entries(AI_UI_I18N))Object.assign(I18N[locale],values);
Object.assign(I18N['zh-Hant'],{candidateWinrates:'候選手 · 多輪搜尋勝率',modelStorageNote:'模型會下載並安裝到 NightyGo 本機模型庫，之後開啟頁面會自動找到。',modelLicense:'模型授權條款',downloadingModel:'正在下載模型',savingModel:'正在儲存模型',savingModelLocally:'正在寫入瀏覽器本機儲存…',modelStorageInsufficient:'本機儲存空間不足，請清出空間或改用較小模型。',modelDownloadLengthMismatch:'模型下載資料長度不完整，請重新下載。',candidateSearchProgress:'候選手 {current}/{total}：正在搜尋 {move}…',candidateSearchSummary:'搜尋 {candidates} 個候選手 · 共 {visits} 次',candidateVisits:'{visits} 次',searching:'搜尋中…',downloadStarting:'正在連線至模型來源…',downloadProgress:'已下載 {loaded} / {total} MB',downloadedSize:'已下載 {loaded} MB',downloadCorsError:'無法下載模型：請確認網路連線後再試。',modelInstalled:'模型已安裝並自動載入'});
Object.assign(I18N['zh-Hans'],{candidateWinrates:'候选手 · 多轮搜索胜率',modelStorageNote:'模型会下载并安装到 NightyGo 本地模型库，之后打开页面会自动找到。',modelLicense:'模型许可条款',downloadingModel:'正在下载模型',savingModel:'正在保存模型',savingModelLocally:'正在写入浏览器本地存储…',modelStorageInsufficient:'本地存储空间不足，请清理空间或改用更小的模型。',modelDownloadLengthMismatch:'模型下载长度不完整，请重新下载。',candidateSearchProgress:'候选手 {current}/{total}：正在搜索 {move}…',candidateSearchSummary:'搜索 {candidates} 个候选手 · 共 {visits} 次',candidateVisits:'{visits} 次',searching:'搜索中…',downloadStarting:'正在连接模型来源…',downloadProgress:'已下载 {loaded} / {total} MB',downloadedSize:'已下载 {loaded} MB',downloadCorsError:'无法下载模型：请确认网络连接后重试。',modelInstalled:'模型已安装并自动加载'});
Object.assign(I18N.en,{candidateWinrates:'Candidate moves · searched win rate',modelStorageNote:'Models install in NightyGo’s local model library and are detected automatically next time.',modelLicense:'Network model license',downloadingModel:'Downloading model',savingModel:'Saving model',savingModelLocally:'Writing to this browser’s storage…',modelStorageInsufficient:'Not enough browser storage is available. Free up space or choose a smaller model.',modelDownloadLengthMismatch:'The downloaded model is incomplete. Please download it again.',candidateSearchProgress:'Searching candidate {current}/{total}: {move}…',candidateSearchSummary:'Searched {candidates} candidate moves · {visits} visits total',candidateVisits:'{visits} visits',searching:'Searching…',downloadStarting:'Connecting to model host…',downloadProgress:'Downloaded {loaded} / {total} MB',downloadedSize:'Downloaded {loaded} MB',downloadCorsError:'Could not download the model. Check your connection and try again.',modelInstalled:'Model installed and loaded'});
Object.assign(I18N.ja,{candidateWinrates:'候補手 · 多重探索の勝率',modelStorageNote:'モデルはNightyGoのローカルライブラリーに保存され、次回から自動検出されます。',modelLicense:'ネットワークモデルのライセンス',downloadingModel:'モデルをダウンロード中',savingModel:'モデルを保存中',savingModelLocally:'ブラウザーのローカルストレージに保存しています…',modelStorageInsufficient:'ブラウザーの空き容量が不足しています。空き容量を増やすか、小さいモデルを選択してください。',modelDownloadLengthMismatch:'モデルが完全にダウンロードされませんでした。もう一度お試しください。',candidateSearchProgress:'候補手 {current}/{total}：{move}を探索中…',candidateSearchSummary:'{candidates}候補を探索 · 合計{visits}回',candidateVisits:'{visits}回',searching:'探索中…',downloadStarting:'モデル配信元に接続中…',downloadProgress:'ダウンロード済み {loaded} / {total} MB',downloadedSize:'ダウンロード済み {loaded} MB',downloadCorsError:'モデルをダウンロードできませんでした。接続を確認して再試行してください。',modelInstalled:'モデルをインストールして読み込みました'});
Object.assign(I18N.ko,{candidateWinrates:'후보 수 · 다중 탐색 승률',modelStorageNote:'모델은 NightyGo 로컬 라이브러리에 설치되며 다음 방문 때 자동으로 감지됩니다.',modelLicense:'네트워크 모델 라이선스',downloadingModel:'모델 다운로드 중',savingModel:'모델 저장 중',savingModelLocally:'이 브라우저의 저장 공간에 기록 중…',modelStorageInsufficient:'브라우저 저장 공간이 부족합니다. 공간을 확보하거나 더 작은 모델을 선택하세요.',modelDownloadLengthMismatch:'모델 다운로드가 완전하지 않습니다. 다시 다운로드해 주세요.',candidateSearchProgress:'후보 {current}/{total}: {move} 탐색 중…',candidateSearchSummary:'후보 {candidates}개 탐색 · 총 {visits}회',candidateVisits:'{visits}회',searching:'탐색 중…',downloadStarting:'모델 서버에 연결 중…',downloadProgress:'다운로드됨 {loaded} / {total} MB',downloadedSize:'다운로드됨 {loaded} MB',downloadCorsError:'모델을 다운로드할 수 없습니다. 연결을 확인한 후 다시 시도하세요.',modelInstalled:'모델 설치 및 로드 완료'});
for(const [locale,values] of Object.entries({
  'zh-Hant':{analysisRunning:'正在分析目前局面…',searchRunning:'AI 正在搜尋落子…',reviewSwing:'第 {move} 手 · 勝率變化 {swing}%',storageLimit:'本機儲存空間不足，請匯出 SGF 保存棋譜。'},
  'zh-Hans':{analysisRunning:'正在分析当前局面…',searchRunning:'AI 正在搜索落子…',reviewSwing:'第 {move} 手 · 胜率变化 {swing}%',storageLimit:'本地存储空间不足，请导出 SGF 保存棋谱。'},
  en:{analysisRunning:'Analyzing this position…',searchRunning:'AI is searching for a move…',reviewSwing:'Move {move} · win-rate change {swing}%',storageLimit:'Local storage is full. Export your SGF to keep a copy.'},
  ja:{analysisRunning:'現在の局面を解析中…',searchRunning:'AIが着手を検索中…',reviewSwing:'{move}手目 · 勝率変動 {swing}%',storageLimit:'ローカル保存領域が不足しています。SGFをエクスポートしてください。'},
  ko:{analysisRunning:'현재 국면 분석 중…',searchRunning:'AI가 착수를 검색 중…',reviewSwing:'{move}수 · 승률 변화 {swing}%',storageLimit:'로컬 저장 공간이 부족합니다. SGF를 내보내 보관하세요.'}
}))Object.assign(I18N[locale],values);
Object.assign(I18N.ja,{gameOver:'両者が連続してパスしました',memoryEstimate:'推定メモリー',memoryUnknown:'メモリー情報を利用できません',boardLabel:'碁盤'});
Object.assign(I18N.ko,{gameOver:'양쪽이 연속으로 패스했습니다',memoryEstimate:'추정 메모리',memoryUnknown:'메모리 정보를 사용할 수 없습니다',boardLabel:'바둑판'});
for(const [locale,values] of Object.entries({
  'zh-Hant':{pageTitle:'NightyGo · 圍棋研習室',metaDescription:'NightyGo 網頁版：對弈、整理棋譜並研究圍棋變化。',brandSubtitle:'圍棋 · 研習室',browserEdition:'網頁版',languageLabel:'語言',firstMove:'第一手',previousMove:'上一步',nextMove:'下一步',lastMove:'最後一手',homeLabel:'NightyGo 首頁',labelText:'標記文字',personalize:'個人化',sgfMetadata:'SGF 棋局資訊',sgfCollection:'SGF 棋譜集合',localInference:'本機推論',sgfMail:'SGF 郵件',unsavedChanges:'尚未儲存的變更',localSgf:'本機 SGF',tagsPlaceholder:'以逗號分隔標籤',tagsAriaLabel:'標籤',lineSecondPoint:'請選擇線段的另一個交點',gameEntry:'{name} · {nodes} 個節點',scoreEstimate:'面積計分估算（未判定死活）：黑 {black} · 白 {white}（含貼目） · {result}',scoreBlack:'黑勝',scoreWhite:'白勝',tagsSaved:'標籤已儲存'},
  'zh-Hans':{pageTitle:'NightyGo · 围棋研习室',metaDescription:'NightyGo 网页版：对弈、整理棋谱并研究围棋变化。',brandSubtitle:'围棋 · 研习室',browserEdition:'网页版',languageLabel:'语言',firstMove:'第一手',previousMove:'上一步',nextMove:'下一步',lastMove:'最后一手',homeLabel:'NightyGo 首页',labelText:'标记文字',personalize:'个性化',sgfMetadata:'SGF 棋局信息',sgfCollection:'SGF 棋谱集合',localInference:'本地推理',sgfMail:'SGF 邮件',unsavedChanges:'尚未保存的更改',localSgf:'本地 SGF',tagsPlaceholder:'用逗号分隔标签',tagsAriaLabel:'标签',lineSecondPoint:'请选择线段的另一个交点',gameEntry:'{name} · {nodes} 个节点',scoreEstimate:'面积计分估算（未判定死活）：黑 {black} · 白 {white}（含贴目） · {result}',scoreBlack:'黑胜',scoreWhite:'白胜',tagsSaved:'标签已保存'},
  en:{pageTitle:'NightyGo · Go Study Studio',metaDescription:'NightyGo browser edition for Go, SGF records, and game study.',brandSubtitle:'GO · STUDY STUDIO',browserEdition:'browser edition',languageLabel:'Language',firstMove:'First move',previousMove:'Previous move',nextMove:'Next move',lastMove:'Last move',homeLabel:'NightyGo home',labelText:'Label text',personalize:'Personalize',sgfMetadata:'SGF metadata',sgfCollection:'SGF collection',localInference:'Local inference',sgfMail:'SGF email',unsavedChanges:'Unsaved changes',localSgf:'Local SGF',tagsPlaceholder:'Tags, separated by commas',tagsAriaLabel:'Tags',lineSecondPoint:'Choose the other endpoint of the line',gameEntry:'{name} · {nodes} nodes',scoreEstimate:'Area score estimate (life and death not checked): Black {black} · White {white} (including komi) · {result}',scoreBlack:'Black wins',scoreWhite:'White wins',tagsSaved:'Tags saved'},
  ja:{pageTitle:'NightyGo · 囲碁研究室',metaDescription:'NightyGoウェブ版。対局、棋譜の整理、囲碁の研究ができます。',brandSubtitle:'囲碁 · 研究室',browserEdition:'ウェブ版',languageLabel:'言語',firstMove:'初手',previousMove:'前の手',nextMove:'次の手',lastMove:'最終手',homeLabel:'NightyGoホーム',labelText:'ラベル文字',personalize:'カスタマイズ',sgfMetadata:'SGF対局情報',sgfCollection:'SGF棋譜コレクション',localInference:'ローカル推論',sgfMail:'SGFメール',unsavedChanges:'未保存の変更',localSgf:'ローカルSGF',tagsPlaceholder:'タグはカンマで区切ります',tagsAriaLabel:'タグ',lineSecondPoint:'線のもう一方の端点を選択してください',gameEntry:'{name} · {nodes}ノード',scoreEstimate:'地計算（死活未判定）：黒 {black} · 白 {white}（コミ込み） · {result}',scoreBlack:'黒の勝ち',scoreWhite:'白の勝ち',tagsSaved:'タグを保存しました'},
  ko:{pageTitle:'NightyGo · 바둑 연구실',metaDescription:'NightyGo 웹 버전. 대국, 기보 정리, 바둑 연구를 할 수 있습니다.',brandSubtitle:'바둑 · 연구실',browserEdition:'웹 버전',languageLabel:'언어',firstMove:'첫 수',previousMove:'이전 수',nextMove:'다음 수',lastMove:'마지막 수',homeLabel:'NightyGo 홈',labelText:'표시 문자',personalize:'개인 설정',sgfMetadata:'SGF 대국 정보',sgfCollection:'SGF 기보 모음',localInference:'로컬 추론',sgfMail:'SGF 이메일',unsavedChanges:'저장되지 않은 변경 사항',localSgf:'로컬 SGF',tagsPlaceholder:'쉼표로 태그 구분',tagsAriaLabel:'태그',lineSecondPoint:'선의 다른 끝점을 선택하세요',gameEntry:'{name} · 노드 {nodes}개',scoreEstimate:'집 계산 (사활 미판정): 흑 {black} · 백 {white} (덤 포함) · {result}',scoreBlack:'흑 승리',scoreWhite:'백 승리',tagsSaved:'태그를 저장했습니다'}
}))Object.assign(I18N[locale],values);
for(const [locale,values] of Object.entries({
  'zh-Hant':{engineWebGpu:'KataGo · WebGPU',engineCpu:'KataGo · CPU',unknownGame:'未命名棋局',gpuAdapterHint:'瀏覽器未回報可用 adapter。請查看瀏覽器的 GPU 診斷頁和平台支援條件。',gpuLinuxAdapterHint:'Linux 版 Chrome 需要啟用 Vulkan。前往 chrome://flags/#enable-vulkan 啟用後重新啟動 Chrome。',gpuAdapterErrorHint:'WebGPU adapter 請求失敗：{error}',profileImportFailed:'無法匯入 AI 設定文件。請確認 JSON 格式與版本正確。',profileJsonInvalid:'AI 設定文件不是有效的 JSON。',profileObjectInvalid:'AI 設定文件必須是 JSON 物件。',profileVersionInvalid:'不支援此 AI 設定文件格式或版本。',profileVisitsInvalid:'搜尋次數必須是 32、128 或 512。',profileTimeInvalid:'單次搜尋時間必須是 5、15 或 30 秒。',handicapBeforeStart:'讓子只能在開始對局前設定。'},
  'zh-Hans':{engineWebGpu:'KataGo · WebGPU',engineCpu:'KataGo · CPU',unknownGame:'未命名棋局',gpuAdapterHint:'浏览器未返回可用 adapter。请查看浏览器的 GPU 诊断页和平台支持条件。',gpuLinuxAdapterHint:'Linux 版 Chrome 需要启用 Vulkan。前往 chrome://flags/#enable-vulkan 启用后重启 Chrome。',gpuAdapterErrorHint:'WebGPU adapter 请求失败：{error}',profileImportFailed:'无法导入 AI 设置文件。请确认 JSON 格式和版本正确。',profileJsonInvalid:'AI 设置文件不是有效的 JSON。',profileObjectInvalid:'AI 设置文件必须是 JSON 对象。',profileVersionInvalid:'不支持此 AI 设置文件格式或版本。',profileVisitsInvalid:'搜索次数必须是 32、128 或 512。',profileTimeInvalid:'单次搜索时间必须是 5、15 或 30 秒。',handicapBeforeStart:'让子只能在开始对局前设置。'},
  en:{engineWebGpu:'KataGo · WebGPU',engineCpu:'KataGo · CPU',unknownGame:'Untitled game',gpuAdapterHint:'The browser returned no adapter. Check its GPU diagnostics and platform support requirements.',gpuLinuxAdapterHint:'Chrome on Linux needs Vulkan enabled. Open chrome://flags/#enable-vulkan, enable Vulkan, then restart Chrome.',gpuAdapterErrorHint:'WebGPU adapter request failed: {error}',profileImportFailed:'Could not import the AI profile. Check that its JSON format and version are supported.',profileJsonInvalid:'The AI profile is not valid JSON.',profileObjectInvalid:'The AI profile must be a JSON object.',profileVersionInvalid:'This AI profile format or version is not supported.',profileVisitsInvalid:'Search visits must be 32, 128, or 512.',profileTimeInvalid:'Search time must be 5, 15, or 30 seconds.',handicapBeforeStart:'Set handicap stones before starting the game.'},
  ja:{engineWebGpu:'KataGo · WebGPU',engineCpu:'KataGo · CPU',unknownGame:'名称未設定の対局',gpuAdapterHint:'ブラウザーから利用可能なadapterが返されませんでした。GPU診断とプラットフォームの要件を確認してください。',gpuLinuxAdapterHint:'Linux版ChromeではVulkanが必要です。chrome://flags/#enable-vulkanで有効にしてChromeを再起動してください。',gpuAdapterErrorHint:'WebGPUアダプターの要求に失敗しました：{error}',profileImportFailed:'AI設定を読み込めません。JSON形式とバージョンを確認してください。',profileJsonInvalid:'AI設定は有効なJSONではありません。',profileObjectInvalid:'AI設定はJSONオブジェクトである必要があります。',profileVersionInvalid:'このAI設定の形式またはバージョンには対応していません。',profileVisitsInvalid:'探索回数は32、128、512のいずれかです。',profileTimeInvalid:'探索時間は5、15、30秒のいずれかです。',handicapBeforeStart:'置き石は対局開始前に設定してください。'},
  ko:{engineWebGpu:'KataGo · WebGPU',engineCpu:'KataGo · CPU',unknownGame:'이름 없는 대국',gpuAdapterHint:'브라우저에서 사용할 수 있는 adapter를 반환하지 않았습니다. GPU 진단과 플랫폼 지원 조건을 확인하세요.',gpuLinuxAdapterHint:'Linux Chrome에서는 Vulkan을 켜야 합니다. chrome://flags/#enable-vulkan에서 활성화하고 Chrome을 다시 시작하세요.',gpuAdapterErrorHint:'WebGPU 어댑터 요청 실패: {error}',profileImportFailed:'AI 설정을 가져오지 못했습니다. JSON 형식과 버전을 확인하세요.',profileJsonInvalid:'AI 설정이 올바른 JSON이 아닙니다.',profileObjectInvalid:'AI 설정은 JSON 객체여야 합니다.',profileVersionInvalid:'지원하지 않는 AI 설정 형식 또는 버전입니다.',profileVisitsInvalid:'탐색 횟수는 32, 128, 512 중 하나여야 합니다.',profileTimeInvalid:'탐색 시간은 5, 15, 30초 중 하나여야 합니다.',handicapBeforeStart:'접바둑 설정은 대국 시작 전에 해주세요.'}
}))Object.assign(I18N[locale],values);
function setAiProgress(key,values={}){aiProgressState={key,values};$('#ai-progress-message').textContent=tr(key,values);$('#ai-progress').hidden=false}
function hideAiProgress(){aiProgressState=null;$('#ai-progress').hidden=true}
function renderReviewResults(){const list=$('#candidate-list');list.innerHTML=reviewResults.length?reviewResults.map(x=>`<li><button class="review-jump" data-move="${x.move}">${tr('reviewSwing',{move:x.move,swing:(x.swing*100).toFixed(1)})}</button></li>`).join(''):`<li>${tr('reviewNoSwing')}</li>`;document.querySelectorAll('.review-jump').forEach(button=>button.onclick=()=>navigateTo(reviewLine[Number(button.dataset.move)]))}
function refreshAiLanguage(){if(aiProgressState)$('#ai-progress-message').textContent=tr(aiProgressState.key,aiProgressState.values);if($('#model-loading-dialog').open)$('#model-loading-status').textContent=tr(modelLoadingStage);if(engineReady)$('#engine-message').textContent=tr(modelBackendGpu?'modelLoadedGpu':'modelLoadedCpu',{version:modelVersion});if(!$('#analysis-results').hidden){if(analysisOutputType==='position'){updateCandidateVisitSummary();$('#score-lead').textContent=tr('scoreLeadWhite',{score:`${lastAnalysisScore>=0?'+':''}${lastAnalysisScore.toFixed(1)}`});renderCandidates()}else{renderReviewResults();$('#engine-message').textContent=tr('reviewComplete',{moves:reviewMoveCount})}}}
function setModelLoadingStatus(key){modelLoadingStage=key;$('#model-loading-status').textContent=tr(key)}
function tr(key,values={}){let value=I18N[language]?.[key]||I18N.en[key]||key;for(const [name,replacement] of Object.entries(values))value=value.replaceAll(`{${name}}`,String(replacement));return value}
function readStore(key,fallback){try{return JSON.parse(localStorage.getItem(key)) ?? fallback}catch{return fallback}}
function writeStore(key,value){try{localStorage.setItem(key,JSON.stringify(value))}catch{toast(tr('storageLimit'))}}
function applyLanguage(){document.documentElement.lang=language;document.title=tr('pageTitle');document.querySelector('meta[name=description]').content=tr('metaDescription');document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=tr(el.dataset.i18n));document.querySelectorAll('[data-i18n-title]').forEach(el=>el.title=tr(el.dataset.i18nTitle));document.querySelectorAll('[data-i18n-aria-label]').forEach(el=>el.setAttribute('aria-label',tr(el.dataset.i18nAriaLabel)));document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>el.placeholder=tr(el.dataset.i18nPlaceholder));$('#language').value=language;$('#library-search').placeholder=tr('librarySearch');if($('#ai-setup-message'))refreshAiSetup();refreshGpuLanguage();refreshAiLanguage()}
function openMailDialog(){const input=$('#mail-address');input.value=localStorage.getItem('ng.mail-address')||'';$('#mail-dialog').showModal();input.focus()}
function sendGameMail(){const input=$('#mail-address'),form=$('#mail-dialog form');if(!form.reportValidity())return;const address=input.value.trim();if(!address)return;localStorage.setItem('ng.mail-address',address);const sgf=serializeCollection();const subject=tr('mailSubject'),body=`${tr('mailBody')}\n\n${sgf}`;const url=`mailto:${encodeURIComponent(address)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;if(url.length>7000){toast(tr('mailTooLarge'));return}$('#mail-dialog').close();window.location.href=url}
function makeRoot(size=19){return {props:{GM:['1'],FF:['4'],CA:['UTF-8'],AP:['NightyGo Web:0.1'],SZ:[String(size)],KM:['6.5']},children:[]}}
function setupNew(size=Number(prefs.size)){if(root&&dirty)saveLibrary(false);pointer=null;touchPreviewAnchor=null;root=makeRoot(size);collectionTrees=[root];current=root;path=[root];dirty=false;rebuild();refresh();writeStore('ng.autosave',serializeCollection())}
function boardSize(){let value=root?.props?.SZ?.[0]||'19';if(value.includes(':'))value=value.split(':')[0];return Math.max(2,Math.min(25,Number(value)||19))}
function emptyBoard(size=boardSize()){return Array.from({length:size},()=>Array(size).fill(0))}
function neighbors(x,y,n){return [[x-1,y],[x+1,y],[x,y-1],[x,y+1]].filter(([a,b])=>a>=0&&b>=0&&a<n&&b<n)}
function groupInfo(grid,x,y){const color=grid[y][x],group=[],lib=new Set(),seen=new Set([`${x},${y}`]),stack=[[x,y]];while(stack.length){const [cx,cy]=stack.pop();group.push([cx,cy]);for(const [nx,ny] of neighbors(cx,cy,grid.length)){if(grid[ny][nx]===0)lib.add(`${nx},${ny}`);else if(grid[ny][nx]===color&&!seen.has(`${nx},${ny}`)){seen.add(`${nx},${ny}`);stack.push([nx,ny])}}}return {group,lib}}
function applyMove(grid,color,x,y,checkKo=false,previous=null){const n=grid.length;if(x<0||y<0||x>=n||y>=n||grid[y][x])throw Error(tr('illegal'));const next=grid.map(r=>r.slice());next[y][x]=color;let captured=[];for(const [nx,ny] of neighbors(x,y,n)){if(next[ny][nx]===3-color){const g=groupInfo(next,nx,ny);if(!g.lib.size){captured.push(...g.group);for(const [gx,gy] of g.group)next[gy][gx]=0}}}if(!groupInfo(next,x,y).lib.size)throw Error(tr('illegal'));if(checkKo&&previous&&sameBoard(next,previous))throw Error(tr('illegal'));return {grid:next,captured}}
function sameBoard(a,b){return a.length===b.length&&a.every((r,y)=>r.every((v,x)=>v===b[y][x]))}
function decodePoint(value,n){if(value.length!==2)throw Error('Invalid SGF coordinate');const x=value.charCodeAt(0)-97,y=value.charCodeAt(1)-97;if(x<0||y<0||x>=n||y>=n)throw Error('SGF coordinate outside board');return [x,y]}
function expandSetup(vals,n){const out=[];for(const val of vals||[]){if(val.includes(':')){const [a,b]=val.split(':').map(v=>decodePoint(v,n));for(let y=Math.min(a[1],b[1]);y<=Math.max(a[1],b[1]);y++)for(let x=Math.min(a[0],b[0]);x<=Math.max(a[0],b[0]);x++)out.push([x,y])}else out.push(decodePoint(val,n))}return out}
function rebuild(){board=emptyBoard();captures={[BLACK]:0,[WHITE]:0};toPlay=BLACK;last=null;positionHistory=[board];for(const node of path){const p=node.props||{};let hadSetup=false;for(const [key,val] of [['AE',0],['AB',BLACK],['AW',WHITE]])for(const [x,y] of expandSetup(p[key],boardSize())){board[y][x]=val;hadSetup=true}if(hadSetup)positionHistory=[board];if(p.PL?.[0])toPlay=p.PL[0]==='W'?WHITE:BLACK;if(p.B||p.W){const color=p.B?BLACK:WHITE;toPlay=color;const value=(p.B||p.W)[0];if(value===''||(value==='tt'&&boardSize()<=19)){last={color,x:null,y:null,pass:true};toPlay=3-color;positionHistory.push(board);continue}const [x,y]=decodePoint(value,boardSize());const result=applyMove(board,color,x,y);board=result.grid;captures[color]+=result.captured.length;last={color,x,y};toPlay=3-color;positionHistory.push(board)}}}
function appendMove(x,y,pass=false){if(path.length>2){const p1=path.at(-1).props,p2=path.at(-2).props;if((p1.B?.[0]===''||p1.W?.[0]==='')&&(p2.B?.[0]===''||p2.W?.[0]==='')){toast(tr('gameOver'));return}}pointer=null;touchPreviewAnchor=null;const color=toPlay,props={};props[color===BLACK?'B':'W']=[pass?'':String.fromCharCode(97+x)+String.fromCharCode(97+y)];const node={props,children:[]};current.children.push(node);current=node;path.push(node);dirty=true;rebuild();if(!pass)playSound(prefs.sound);refresh()}
function navigateTo(target){const found=[];function search(node){found.push(node);if(node===target)return true;for(const c of node.children||[])if(search(c))return true;found.pop();return false}if(search(root)){pointer=null;touchPreviewAnchor=null;path=found;current=target;rebuild();refresh()}}
function previous(){if(path.length>1){path.pop();current=path.at(-1);rebuild();refresh()}}
function next(index=0){if(current.children?.length){const nextNode=current.children[index]||current.children[0];path.push(nextNode);current=nextNode;rebuild();refresh()}else toast(tr('noBranch'))}
function updateComment(value){if(value.trim())current.props.C=[value];else delete current.props.C;dirty=true;refreshTree();writeStore('ng.autosave',serializeCollection())}
function setProp(key,value){if(value==='')delete root.props[key];else root.props[key]=[value];dirty=true;refresh()}
function serialize(node){return serializeSgf(node)}
function serializeCollection(){return collectionTrees.map(serialize).join("\n")}
function downloadSgf(){const data=serializeCollection();const blob=new Blob([data],{type:'application/x-go-sgf;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${safeName(root.props.PB?.[0]||'nightygo')}-${new Date().toISOString().slice(0,10)}.sgf`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);dirty=false;refresh();toast(tr('saved'));saveLibrary(true)}
function handicapPoints(size,count){const star=size===19?[3,9,15]:size===13?[3,6,9]:[2,4,6];const [lo,mid,hi]=star;return [[hi,lo],[lo,hi],[lo,lo],[hi,hi],[mid,mid],[mid,lo],[mid,hi],[lo,mid],[hi,mid]].slice(0,count).map(([x,y])=>String.fromCharCode(97+x)+String.fromCharCode(97+y))}
function estimateAreaScore(){
  const size=boardSize(),ownership=Array(size*size).fill(0),seen=new Set();let black=0,white=0;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    if(board[y][x]===BLACK){black++;continue}if(board[y][x]===WHITE){white++;continue}
    const key=`${x},${y}`;if(seen.has(key))continue;
    const region=[],border=new Set(),stack=[[x,y]];seen.add(key);
    while(stack.length){const [cx,cy]=stack.pop();region.push([cx,cy]);for(const [nx,ny] of neighbors(cx,cy,size)){if(board[ny][nx])border.add(board[ny][nx]);else{const nextKey=`${nx},${ny}`;if(!seen.has(nextKey)){seen.add(nextKey);stack.push([nx,ny])}}}}
    const owner=border.size===1?[...border][0]:0;
    if(owner===BLACK)black+=region.length;else if(owner===WHITE)white+=region.length;
    if(owner)for(const [rx,ry] of region)ownership[ry*size+rx]=owner;
  }
  const komi=Number(root.props.KM?.[0]||7.5);white+=komi;
  const diff=Math.abs(black-white),winner=black>white?'B':'W';
  return {ownership,black,white,komi,diff,winner,result:`${winner}+${diff.toFixed(1)}`};
}
function scoreGame(){
  if(showRuleEstimate){showRuleEstimate=false;ruleEstimate=null;ruleOwnershipMap=null;ruleEstimateBoard=null;ruleEstimateNode=null;toast(tr('overlayHidden'))}
  else{ruleEstimate=estimateAreaScore();ruleOwnershipMap=ruleEstimate.ownership;ruleEstimateBoard=board;ruleEstimateNode=current;showRuleEstimate=true;toast(tr('scoreEstimate',{black:ruleEstimate.black.toFixed(1),white:ruleEstimate.white.toFixed(1),result:tr(ruleEstimate.winner==='B'?'scoreBlack':'scoreWhite')+' '+ruleEstimate.diff.toFixed(1)}),6500)}
  updateOverlayToggles();drawBoard();
}
function toggleAiOwnership(){if(!ownershipMap?.length)return;showAiOwnership=!showAiOwnership;updateOverlayToggles();drawBoard()}
function updateOverlayToggles(){
  const ruleButton=$('#score-game'),aiButton=$('#ai-territory-toggle'),badge=$('#board-estimate');
  if(ruleButton){ruleButton.setAttribute('aria-pressed',String(showRuleEstimate));ruleButton.classList.toggle('active',showRuleEstimate)}
  if(aiButton){aiButton.disabled=!ownershipMap?.length;if(aiButton.disabled)showAiOwnership=false;aiButton.setAttribute('aria-pressed',String(showAiOwnership));aiButton.classList.toggle('active',showAiOwnership)}
  if(badge){const lines=[];if(showRuleEstimate&&ruleEstimate)lines.push(tr('boardOverlayRule',{black:ruleEstimate.black.toFixed(1),white:ruleEstimate.white.toFixed(1)}));if(showAiOwnership&&ownershipMap?.length)lines.push(tr('boardOverlayAi'));badge.textContent=lines.join('  •  ');badge.hidden=!lines.length}
}

function safeName(s){return s.toLowerCase().replace(/[^a-z0-9-_]+/g,'-').replace(/^-|-$/g)||'game'}
function saveLibrary(toastIt=true){if(!root)return;const sgf=serializeCollection(),meta=root.props;const title=`${meta.PB?.[0]||'Black'} – ${meta.PW?.[0]||'White'}`;const old=library.find(g=>g.sgf===sgf);library=[{id:old?.id||Date.now(),title,event:meta.EV?.[0]||'',result:meta.RE?.[0]||'',tags:old?.tags||[],sgf,updated:new Date().toISOString()},...library.filter(g=>g.sgf!==sgf)].slice(0,100);writeStore('ng.library',library);writeStore('ng.autosave',sgf);dirty=false;refreshLibrary();refreshHeader();if(toastIt)toast(tr('saveFirst'))}
function loadSgfTree(tree, collection=[tree]){collectionTrees=collection;root=tree;current=root;path=[root];while(current.children?.length){current=current.children[0];path.push(current)}dirty=false;rebuild();refresh();writeStore('ng.autosave',serializeCollection());toast(tr('loaded'))}
function refresh(){if(ruleEstimate&&(ruleEstimateBoard!==board||ruleEstimateNode!==current)){ruleEstimate=null;ruleOwnershipMap=null;ruleEstimateBoard=null;ruleEstimateNode=null;showRuleEstimate=false}if(engineBoardSize&&engineBoardSize!==boardSize()){engineWorker?.terminate();engineWorker=null;engineBoardSize=0;engineReady=false;analyzedNode=null;analyzedBoard=null;ownershipMap=null;showAiOwnership=false;candidateAnalysis=[];$('#analyze-position').disabled=true;$('#play-ai').disabled=true;$('#review-game').disabled=true;$('#engine-message').textContent=tr('boardSizeChanged')}if(analyzedNode&&(analyzedNode!==current||analyzedBoard!==board)){analyzedNode=null;analyzedBoard=null;ownershipMap=null;showAiOwnership=false;candidateAnalysis=[];$('#analysis-results').hidden=true;$('#candidate-list').replaceChildren();$('#ai-empty').hidden=false;if(engineReady)$('#engine-message').textContent=tr('positionChanged')}updateOverlayToggles();refreshBoard();refreshHeader();refreshControls();refreshTree();refreshInfo();refreshLibrary();$('#comment').value=current.props.C?.join('\n')||'';$('#tree-count').textContent=countNodes(root);$('#move-position').textContent=`${path.length-1} / ${countNodes(root)-1}`;$('#undo').disabled=path.length<=1;$('#redo').disabled=!current.children?.length;$('#previous').disabled=path.length<=1;$('#next').disabled=!current.children?.length;if(dirty)writeStore('ng.autosave',serializeCollection())}
function restorePanelOrder(){const panelBox=$('#side-panels'),fallback=['analysis-panel','tree-panel','info-panel'];let order=readStore('ng.panel-order',fallback);if(!Array.isArray(order)||new Set(order).size!==fallback.length||fallback.some(id=>!order.includes(id)))order=fallback;for(const id of order){const panel=document.getElementById(id);if(panel)panelBox.append(panel)}}
function savePanelOrder(){writeStore('ng.panel-order',[...$('#side-panels').children].map(panel=>panel.id))}
function bindPanelReordering(){
  const box=$('#side-panels'),panels=[...box.querySelectorAll(':scope > .panel')],desktop=matchMedia('(min-width: 791px)');
  const clearIndicators=()=>box.querySelectorAll('.drop-before,.drop-after').forEach(node=>node.classList.remove('drop-before','drop-after'));
  const movePanel=(moving,x,y)=>{let target=document.elementFromPoint(x,y)?.closest('.panel');if(target===moving)target=null;target ||= panels.map(panel=>({panel,rect:panel.getBoundingClientRect()})).filter(item=>item.panel!==moving).sort((a,b)=>Math.abs(a.rect.top+a.rect.height/2-y)-Math.abs(b.rect.top+b.rect.height/2-y))[0]?.panel;if(!target||target===moving)return;const rect=target.getBoundingClientRect(),after=y>rect.top+rect.height/2;box.insertBefore(moving,after?target.nextSibling:target);clearIndicators();target.classList.add(after?'drop-after':'drop-before')};
  for(const panel of panels){
    panel.addEventListener('pointerdown',event=>{panel.dataset.dragReady=String(Boolean(event.target.closest('.panel-drag-handle')&&desktop.matches))});
    panel.addEventListener('dragstart',event=>{if(!desktop.matches||panel.dataset.dragReady!=='true'){event.preventDefault();return}panel.classList.add('is-dragging');event.dataTransfer.effectAllowed='move';event.dataTransfer.setData('text/plain',panel.id)});
    panel.addEventListener('dragover',event=>{const moving=box.querySelector('.is-dragging'),target=event.target.closest('.panel');if(!moving||!target||moving===target)return;event.preventDefault();const after=event.clientY>target.getBoundingClientRect().top+target.offsetHeight/2;box.insertBefore(moving,after?target.nextSibling:target);clearIndicators();target.classList.add(after?'drop-after':'drop-before')});
    panel.addEventListener('dragend',()=>{panel.classList.remove('is-dragging');clearIndicators();delete panel.dataset.dragReady;savePanelOrder()});
    panel.querySelector('.panel-drag-handle')?.addEventListener('pointerdown',event=>{if(event.pointerType!=='touch')return;event.preventDefault();const handle=event.currentTarget;handle.setPointerCapture(event.pointerId);panel.classList.add('is-dragging');const onMove=moveEvent=>movePanel(panel,moveEvent.clientX,moveEvent.clientY);const finish=()=>{document.removeEventListener('pointermove',onMove);handle.removeEventListener('pointerup',finish);handle.removeEventListener('pointercancel',finish);panel.classList.remove('is-dragging');clearIndicators();savePanelOrder()};document.addEventListener('pointermove',onMove);handle.addEventListener('pointerup',finish,{once:true});handle.addEventListener('pointercancel',finish,{once:true})});
  }
  box.querySelectorAll('.panel-drag-handle').forEach(handle=>handle.addEventListener('keydown',event=>{if(!event.altKey||!['ArrowUp','ArrowDown'].includes(event.key))return;event.preventDefault();const panel=handle.closest('.panel'),sibling=event.key==='ArrowUp'?panel.previousElementSibling:panel.nextElementSibling;if(!sibling)return;box.insertBefore(panel,event.key==='ArrowUp'?sibling:sibling.nextSibling);savePanelOrder();handle.focus()}));
}
function countNodes(node){return 1+(node.children||[]).reduce((a,c)=>a+countNodes(c),0)}
function refreshHeader(){const p=root.props;$('#game-name').textContent=p.GN?.[0]||`${p.PB?.[0]||tr('blackPlayer')}${tr('versus')}${p.PW?.[0]||tr('whitePlayer')}`;$('#game-meta').innerHTML=`${boardSize()} × ${boardSize()} <span>·</span> ${dirty?tr('unsaved'):(p.DT?.[0]||tr('unsaved'))}`}
function refreshControls(){$('#turn-label').textContent=tr(toPlay===BLACK?'blackTurn':'whiteTurn');$('#turn-pill .stone-chip').className=`stone-chip ${toPlay===BLACK?'black':'white'}`;$('#black-captures').textContent=captures[BLACK];$('#white-captures').textContent=captures[WHITE];$('#move-count').textContent=Math.max(0,path.length-1);$('#game-meta').setAttribute('title',dirty?tr('unsavedChanges'):'')}
function refreshInfo(){const p=root.props;$('#info-black').textContent=p.PB?.[0]||'—';$('#info-white').textContent=p.PW?.[0]||'—';$('#info-event').textContent=p.EV?.[0]||'—';$('#info-result').textContent=p.RE?.[0]||'—';$('#info-komi').textContent=p.KM?.[0]||'—'}
function refreshLibrary(){const q=$('#library-search').value.toLocaleLowerCase();const found=library.filter(g=>(g.title+' '+g.event+' '+g.result+' '+(g.tags||[]).join(' ')).toLocaleLowerCase().includes(q));$('#library-list').innerHTML=found.length?found.map(g=>`<article class="library-card" data-lib="${g.id}"><b>${escapeHtml(g.title)}</b><span>${escapeHtml(g.event||tr('localSgf'))} · ${escapeHtml(g.result||'—')}</span><input class="library-tags" data-tags="${g.id}" value="${escapeHtml((g.tags||[]).join(', '))}" placeholder="${tr('tagsPlaceholder')}" aria-label="${tr('tagsAriaLabel')}" /></article>`).join(''):`<div class="library-empty">${tr('noGames')}</div>`;document.querySelectorAll('[data-lib]').forEach(el=>el.onclick=e=>{if(e.target.matches('.library-tags'))return;const g=library.find(v=>v.id===Number(el.dataset.lib));if(g)try{const games=parseSgf(g.sgf);loadSgfTree(games[0],games)}catch{toast(tr('badSgf'))}});document.querySelectorAll('.library-tags').forEach(input=>input.onchange=()=>{const g=library.find(v=>v.id===Number(input.dataset.tags));if(g){g.tags=input.value.split(',').map(t=>t.trim()).filter(Boolean);writeStore('ng.library',library);toast(tr('tagsSaved'))}})}
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
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.clearRect(0, 0, width, height);
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
  } else if (prefs.board === 'mimi') {
    ctx.drawImage(getBoardTexture('mimi'), 0, 0, width, height);
  } else {
    ctx.drawImage(getBoardTexture(prefs.board), 0, 0, width, height);
    drawAnimatedSky(ctx, width, elapsed);
  }
  const lineColor = prefs.board === 'wood' ? 'rgba(64,44,25,.85)' : prefs.board === 'mimi' ? 'rgba(105,61,39,.82)' : 'rgba(203,219,245,.68)';
  ctx.strokeStyle = lineColor;
  ctx.lineWidth = Math.max(1.2, width * .0015);
  for (let index = 0; index < size; index++) {
    const point = pad + index * step;
    ctx.beginPath(); ctx.moveTo(pad, point); ctx.lineTo(width - pad, point); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(point, pad); ctx.lineTo(point, height - pad); ctx.stroke();
  }
  if ([9, 13, 19].includes(size)) {
    const stars = size === 19 ? [3, 9, 15] : size === 13 ? [3, 6, 9] : [2, 4, 6];
    const dotRadius = Math.max(width * .0055, step * .105);
    const dotColor = prefs.board === 'wood' ? '#543919' : prefs.board === 'mimi' ? '#a54f2d' : '#e5efff';
    const haloColor = prefs.board === 'wood' ? 'rgba(255,240,204,.86)' : prefs.board === 'mimi' ? 'rgba(255,248,235,.94)' : 'rgba(12,20,42,.9)';
    for (const x of stars) for (const y of stars) {
      const px = pad + x * step, py = pad + y * step;
      ctx.fillStyle = haloColor;
      ctx.beginPath(); ctx.arc(px, py, dotRadius * 1.38, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = dotColor;
      ctx.beginPath(); ctx.arc(px, py, dotRadius * .76, 0, Math.PI * 2); ctx.fill();
    }
  }
  if (showRuleEstimate && ruleOwnershipMap?.length === size * size) {
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const owner = ruleOwnershipMap[y * size + x];
      if (!owner || board[y]?.[x]) continue;
      ctx.fillStyle = owner === BLACK ? 'rgba(40, 49, 63, .30)' : 'rgba(235, 139, 95, .34)';
      ctx.beginPath(); ctx.arc(pad + x * step, pad + y * step, step * .28, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = owner === BLACK ? 'rgba(21, 28, 40, .46)' : 'rgba(181, 91, 52, .48)';
      ctx.lineWidth = Math.max(1, step * .025); ctx.stroke();
    }
  }
  if (showAiOwnership && ownershipMap?.length === size * size) {
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const owner = ownershipMap[y * size + x];
      if (Math.abs(owner) <= .2) continue;
      ctx.fillStyle = owner > 0 ? `rgba(100,170,255,${Math.min(.48, Math.abs(owner) * .5)})` : `rgba(255,145,95,${Math.min(.48, Math.abs(owner) * .5)})`;
      ctx.beginPath(); ctx.arc(pad + x * step, pad + y * step, step * .14, 0, Math.PI * 2); ctx.fill();
    }
  }
  const previewValid = $('#markup-tool')?.value === 'none' && pointer && pointer.x >= 0 && pointer.y >= 0 && pointer.x < size && pointer.y < size && !board[pointer.y]?.[pointer.x];
  if (previewValid && pointer.touchPreview) {
    const x = pad + pointer.x * step, y = pad + pointer.y * step;
    ctx.save();
    ctx.strokeStyle = ['wood', 'mimi'].includes(prefs.board) ? 'rgba(73, 47, 35, .86)' : 'rgba(238, 246, 255, .9)';
    ctx.lineWidth = Math.max(1.5, width * .0024);
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(width - pad, y);
    ctx.moveTo(x, pad); ctx.lineTo(x, height - pad); ctx.stroke();
    ctx.restore();
  }
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    if (board[y]?.[x]) paintStone(ctx, pad + x * step, pad + y * step, step * .455, board[y][x]);
  }
  if(candidateAnalysis.length){ctx.save();ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`700 ${Math.max(9,step*.22)}px Manrope, sans-serif`;candidateAnalysis.forEach((candidate,index)=>{if(candidate.loc>=size*size||candidate.winrate===null)return;const x=pad+(candidate.loc%size)*step,y=pad+Math.floor(candidate.loc/size)*step;ctx.fillStyle='rgba(13,21,36,.86)';ctx.strokeStyle=index===0?'#8debd4':'#a7c5ff';ctx.lineWidth=Math.max(1.5,step*.035);ctx.beginPath();ctx.arc(x,y,step*.28,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle='#f4f7ff';ctx.fillText(`${(candidate.winrate*100).toFixed(0)}%`,x,y)});ctx.restore()}
  drawMarkups(ctx, pad, step);
  if (last && !last.pass) {
    const x = pad + last.x * step, y = pad + last.y * step;
    ctx.strokeStyle = last.color === BLACK ? '#f7e0ad' : '#283244';
    ctx.lineWidth = Math.max(1.2, width * .0024);
    ctx.beginPath(); ctx.arc(x, y, step * .19, 0, Math.PI * 2); ctx.stroke();
  }
  if (previewValid) {
    ctx.save();
    ctx.globalAlpha = pointer.touchPreview ? .28 : .46;
    paintStone(ctx, pad + pointer.x * step, pad + pointer.y * step, step * .455, toPlay);
    ctx.restore();
  }
  ctx.restore();
  scheduleAmbientFrame();
}
const boardTextureCache = new Map();
function getBoardTexture(material) {
  if (boardTextureCache.has(material)) return boardTextureCache.get(material);
  const size = 512;
  const texture = document.createElement('canvas');
  texture.width = texture.height = size;
  const ctx = texture.getContext('2d');
  let seed = material === 'starfield' ? 951 : material === 'mimi' ? 842 : 461;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const paintNebula = (x, y, color) => {
    const [red, green, blue] = color;
    const glow = ctx.createRadialGradient(x, y, 0, x, y, 170);
    glow.addColorStop(0, `rgba(${red},${green},${blue},.37)`);
    glow.addColorStop(1, `rgba(${red},${green},${blue},0)`);
    ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, 170, 0, Math.PI * 2); ctx.fill();
  };
  if (material === 'mimi') {
    const cream = ctx.createLinearGradient(0, 0, size, size);
    cream.addColorStop(0, '#fff4e1'); cream.addColorStop(.48, '#f4dfc4'); cream.addColorStop(1, '#f8e9d4');
    ctx.fillStyle = cream; ctx.fillRect(0, 0, size, size);
    const glow = ctx.createRadialGradient(size * .5, size * .48, size * .08, size * .5, size * .48, size * .72);
    glow.addColorStop(0, 'rgba(255,255,255,.05)'); glow.addColorStop(1, 'rgba(225,137,83,.22)');
    ctx.fillStyle = glow; ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = 'rgba(181,111,66,.07)'; ctx.lineWidth = 1;
    for (let index = 0; index < 42; index++) {
      const y = (index * 37) % size;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.bezierCurveTo(size * .3, y + Math.sin(index) * 4, size * .7, y + Math.cos(index) * 5, size, y); ctx.stroke();
    }
    const paw = (x, y, scale) => {
      ctx.save(); ctx.translate(x, y); ctx.scale(scale, scale); ctx.fillStyle = 'rgba(203,126,79,.14)';
      ctx.beginPath(); ctx.ellipse(0, 4, 7, 5.5, 0, 0, Math.PI * 2); ctx.fill();
      for (const [toeX, toeY] of [[-7,-4],[-2,-8],[4,-8],[9,-4]]) { ctx.beginPath(); ctx.arc(toeX, toeY, 2.6, 0, Math.PI * 2); ctx.fill(); }
      ctx.restore();
    };
    for (const [x, y, scale] of [[38,44,.8],[470,66,.7],[72,458,.72],[445,430,.85],[255,42,.55],[266,474,.56]]) paw(x,y,scale);
  } else if (material === 'starfield') {
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
  if (['wood', 'mimi'].includes(prefs.board) || prefs.motion === 'off' || document.visibilityState !== 'visible') {
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
function paintMimiCatStone(ctx, x, y, radius, color) {
  const black = color === BLACK;
  const stone = ctx.createRadialGradient(x - radius * .34, y - radius * .42, radius * .05, x, y, radius * 1.12);
  if (black) { stone.addColorStop(0, '#747986'); stone.addColorStop(.3, '#353a45'); stone.addColorStop(.78, '#171a20'); stone.addColorStop(1, '#07090d'); }
  else { stone.addColorStop(0, '#fff'); stone.addColorStop(.55, '#f4f5f5'); stone.addColorStop(.88, '#d7dbe0'); stone.addColorStop(1, '#aab0b8'); }
  const earStroke = black ? 'rgba(255,255,255,.22)' : 'rgba(82,89,99,.34)';
  ctx.save();
  ctx.shadowColor = 'rgba(20, 17, 17, .42)'; ctx.shadowBlur = radius * .28; ctx.shadowOffsetY = radius * .16;
  ctx.fillStyle = stone;
  for (const side of [-1, 1]) {
    ctx.beginPath();
    ctx.moveTo(x + side * radius * .43, y - radius * .48);
    ctx.quadraticCurveTo(x + side * radius * .67, y - radius * 1.32, x + side * radius * .96, y - radius * 1.12);
    ctx.quadraticCurveTo(x + side * radius * 1.05, y - radius * .76, x + side * radius * .78, y - radius * .26);
    ctx.closePath(); ctx.fill(); ctx.strokeStyle = earStroke; ctx.lineWidth = Math.max(.55, radius * .04); ctx.stroke();
  }
  ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.strokeStyle = earStroke; ctx.lineWidth = Math.max(.7, radius * .045);
  ctx.beginPath(); ctx.arc(x, y, radius * .97, 0, Math.PI * 2); ctx.stroke();
  for (const side of [-1, 1]) {
    ctx.beginPath();
    ctx.moveTo(x + side * radius * .56, y - radius * .67);
    ctx.quadraticCurveTo(x + side * radius * .76, y - radius * 1.08, x + side * radius * .86, y - radius * .92);
    ctx.quadraticCurveTo(x + side * radius * .87, y - radius * .76, x + side * radius * .72, y - radius * .58);
    ctx.closePath();
    ctx.fillStyle = black ? 'rgba(240,156,163,.74)' : 'rgba(237,157,151,.66)'; ctx.fill();
  }
  paintSphereLighting(ctx, x, y, radius);
  ctx.restore();
}
function paintStone(ctx, x, y, radius, color) {
  if (prefs.stones === 'mimi') { paintMimiCatStone(ctx, x, y, radius, color); return; }
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
function drawMarkups(ctx,pad,space){const props=current?.props||{},n=boardSize(),ink=['wood','mimi'].includes(prefs.board)?'#70432f':'#e5dcff';ctx.save();ctx.lineWidth=Math.max(1.5,space*.07);ctx.strokeStyle=ink;ctx.fillStyle=ink;for(const key of ['LN','AR'])for(const value of props[key]||[]){try{const [from,to]=value.split(':');const [x1,y1]=decodePoint(from,n),[x2,y2]=decodePoint(to,n);const a={x:pad+x1*space,y:pad+y1*space},b={x:pad+x2*space,y:pad+y2*space};ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();if(key==='AR'){const angle=Math.atan2(b.y-a.y,b.x-a.x),r=space*.24;ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-r*Math.cos(angle-.5),b.y-r*Math.sin(angle-.5));ctx.lineTo(b.x-r*Math.cos(angle+.5),b.y-r*Math.sin(angle+.5));ctx.closePath();ctx.fill()}}catch{}}
 for(const key of ['TR','SQ','CR','MA','LB'])for(const value of props[key]||[]){try{const coordinate=key==='LB'?value.slice(0,2):value,[x,y]=decodePoint(coordinate,n),cx=pad+x*space,cy=pad+y*space,r=space*.22;ctx.beginPath();if(key==='TR'){ctx.moveTo(cx,cy-r);ctx.lineTo(cx-r,cy+r);ctx.lineTo(cx+r,cy+r);ctx.closePath();ctx.stroke()}else if(key==='SQ'){ctx.strokeRect(cx-r,cy-r,r*2,r*2)}else if(key==='CR'){ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke()}else if(key==='MA'){ctx.moveTo(cx-r,cy-r);ctx.lineTo(cx+r,cy+r);ctx.moveTo(cx+r,cy-r);ctx.lineTo(cx-r,cy+r);ctx.stroke()}else{ctx.font=`600 ${space*.26}px sans-serif`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(value.slice(3)||'A',cx,cy)}}catch{}}ctx.restore()}
function addMarkup(x,y){const key=$('#markup-tool').value;if(key==='none')return false;const point=String.fromCharCode(97+x)+String.fromCharCode(97+y),property=current.props[key]||[],label=$('#markup-label').value.trim()||'A';if(key==='LN'||key==='AR'){if(!pendingLinePoint){pendingLinePoint=point;toast(tr('lineSecondPoint'));return true}const value=`${pendingLinePoint}:${point}`;pendingLinePoint=null;property.push(value);current.props[key]=property;dirty=true;refresh();return true}const value=key==='LB'?`${point}:${label}`:point,index=property.findIndex(v=>key==='LB'?v.slice(0,2)===point:v===point);if(index>=0)property.splice(index,1);else property.push(value);if(property.length)current.props[key]=property;else delete current.props[key];dirty=true;refresh();return true}
function boardPoint(clientX,clientY){const r=$('#go-board').getBoundingClientRect(),n=boardSize(),pad=r.width*.063,space=(r.width-pad*2)/(n-1);const x=Math.round((clientX-r.left-pad)/space),y=Math.round((clientY-r.top-pad)/space);return {x,y,distance:Math.hypot(clientX-r.left-(pad+x*space),clientY-r.top-(pad+y*space)),n}}
function playSound(which){if(which==='off')return;const source=which==='meow'?'assets/sounds/cat_meow.mp3':`assets/sounds/go_stone_${which}.wav`;const audio=new Audio(source);audio.volume=.55;audio.play().catch(()=>{})}
function playCapture(count){if(!count)return;const key=count===1?'capture_single':count<=3?'capture_small_group':count<=7?'capture_group':'capture_large_group';const a=new Audio(`assets/sounds/${key}.wav`);a.volume=.55;a.play().catch(()=>{})}
let toastTimer;function toast(message,duration=2300){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),duration)}
function refreshGpuLanguage(){const tag=$('#gpu-status');tag.className='status-tag';if(gpuReason==='checking'){tag.textContent=tr('gpuChecking');tag.title='';return}if(gpuReason==='secure'){tag.textContent=tr('gpuSecureRequired');tag.title=tr('gpuSecureHint');return}if(gpuReason==='unsupported'){tag.textContent=tr('gpuMissing');tag.title=tr('gpuUnsupportedHint');return}if(gpuReason==='missingAdapter'){tag.textContent=tr('gpuAdapterMissing');const platform=(navigator.userAgentData?.platform||navigator.platform||'').toLowerCase();tag.title=platform.includes('linux')&&navigator.userAgent.includes('Chrome')?tr('gpuLinuxAdapterHint'):tr('gpuAdapterHint');return}if(gpuReason==='error'){tag.textContent=tr('gpuMissing');tag.title=tr('gpuAdapterErrorHint',{error:gpuError});return}if(engineReady){tag.textContent=tr(modelBackendGpu?'engineWebGpu':'engineCpu');tag.classList.add('ready');return}tag.textContent=tr('gpuAvailable');tag.classList.add('ready');tag.title=tr('enginePending')}
async function checkGpu(){gpuReason='checking';gpuState='unknown';refreshGpuLanguage();if(!globalThis.isSecureContext){gpuState='unavailable';gpuReason='secure';refreshGpuLanguage();refreshAiSetup();return}if(!navigator.gpu){gpuState='unavailable';gpuReason='unsupported';refreshGpuLanguage();refreshAiSetup();return}try{const adapter=await navigator.gpu.requestAdapter();if(!adapter){gpuState='unavailable';gpuReason='missingAdapter';refreshGpuLanguage();refreshAiSetup();return}gpuState='available';gpuReason='available';refreshGpuLanguage();refreshAiSetup()}catch(error){gpuState='unavailable';gpuReason='error';gpuError=error.message||String(error);refreshGpuLanguage();refreshAiSetup()}}
function applyInterfaceTheme(theme){document.body.classList.toggle('light',theme==='light');document.body.classList.toggle('mimi',theme==='mimi')}
function applyPrefs(){document.documentElement.style.setProperty('--font',`${prefs.font}px`);applyInterfaceTheme(prefs.theme);$('#theme').value=prefs.theme;$('#board-material').value=prefs.board;$('#stone-material').value=prefs.stones;const activeSize=root?boardSize():prefs.size;if(!Array.from($('#board-size').options).some(o=>Number(o.value)===activeSize))$('#board-size').add(new Option(activeSize,activeSize));$('#board-size').value=String(activeSize);$('#font-size').value=prefs.font;$('#font-value').value=`${prefs.font} px`;$('#placement-sound').value=prefs.sound;$('#motion').value=prefs.motion;drawBoard();drawStonePreviews()}
function drawStonePreviews(){for(const [selector,color] of [['#stone-preview-black',BLACK],['#stone-preview-white',WHITE]]){const canvas=$(selector);if(!canvas)continue;const context=canvas.getContext('2d');context.clearRect(0,0,canvas.width,canvas.height);context.save();context.scale(canvas.width/96,canvas.height/72);paintStone(context,48,36,25,color);context.restore()}}
function openSettings(){const d=$('#settings-dialog');d.dataset.before=JSON.stringify(prefs);applyPrefs();d.showModal()}
function restoreSettings(){const before=$('#settings-dialog').dataset.before;if(before){prefs=JSON.parse(before);applyPrefs()}}
function showGameChooser(games){const dialog=$('#game-chooser');const select=$('#game-choice');select.innerHTML=games.map((g,i)=>{const name=escapeHtml(g.props.GN?.[0]||g.props.PB?.[0]||tr('unknownGame'));return `<option value="${i}">${i+1}. ${tr('gameEntry',{name,nodes:countNodes(g)})}</option>`}).join('');dialog.showModal();$('#choose-game').onclick=()=>{const index=Number(select.value);loadSgfTree(games[index],games)}}
function bind(){
 $('#language').onchange=e=>{language=e.target.value;localStorage.removeItem(LANGUAGE_COOKIE);saveLanguageCookie(language);applyLanguage();refresh();refreshModels().catch(error=>console.warn('Could not refresh localized model list',error))};$('#settings-open').onclick=openSettings;
 $('#new-game').onclick=()=>{if(dirty)saveLibrary(false);setupNew(Number(prefs.size))};$('#import-button').onclick=()=>$('#file-input').click();$('#file-input').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{if(dirty)saveLibrary(false);const bytes=await f.arrayBuffer();const header=new TextDecoder('ascii').decode(bytes.slice(0,8192));const charset=header.match(/\bCA\[([^\]]+)\]/)?.[1]||'ISO-8859-1';let contents;try{contents=new TextDecoder(charset).decode(bytes)}catch{contents=new TextDecoder('utf-8').decode(bytes)}const games=parseSgf(contents);loadSgfTree(games[0],games);if(games.length>1)showGameChooser(games)}catch(err){console.error(err);toast(tr('badSgf'))}e.target.value=''};
 $('#save-sgf').onclick=downloadSgf;$('#send-mail').onclick=openMailDialog;$('#mail-address').oninput=e=>{if(e.target.checkValidity()&&e.target.value.trim())localStorage.setItem('ng.mail-address',e.target.value.trim())};$('#open-mail').onclick=sendGameMail;$('#score-game').onclick=scoreGame;$('#ai-territory-toggle').onclick=toggleAiOwnership;$('#undo').onclick=previous;$('#redo').onclick=()=>next(0);$('#previous').onclick=previous;$('#next').onclick=()=>next(0);$('#first').onclick=()=>navigateTo(root);$('#last').onclick=()=>{let n=root;while(n.children?.length)n=n.children[0];navigateTo(n)};$('#pass').onclick=()=>appendMove(0,0,true);$('#main-line').onclick=()=>{$('#main-line').classList.toggle('active');refreshTree()};$('#collapse-tree').onclick=()=>{treePan.x=0;treePan.y=0;$('#tree-scroll').scrollTo({left:0,top:0,behavior:'smooth'});refreshTree()};bindTreePan();$('#review-game').onclick=reviewGame;$('#check-gpu').onclick=checkGpu;$('#model-center').onclick=openModelCenter;document.querySelectorAll('[data-model-url]').forEach(button=>button.onclick=()=>downloadOfficialModel(button.dataset.modelUrl,button.dataset.modelName).catch(()=>{}));$('#model-file').onchange=e=>importModel(e.target.files[0]).catch(err=>toast(err.message));$('#save-ai-config').onclick=downloadAiConfig;$('#export-ai-config').onclick=()=>{const config=storedAiConfig();if(!config)return;const blob=new Blob([JSON.stringify(config,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='nightygo-ai-profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};$('#ai-config-file').onchange=e=>importAiConfig(e.target.files[0]).catch(err=>toast(err.message));$('#search-visits').onchange=refreshAiSetup;$('#search-time').onchange=refreshAiSetup;$('#load-model').onclick=()=>loadSelectedModel().catch(err=>toast(err.message));$('#analyze-position').onclick=analyzePosition;$('#play-ai').onclick=playAiMove;
 $('#markup-tool').onchange=e=>{pendingLinePoint=null;$('#markup-label').disabled=e.target.value!=='LB';drawBoard()};$('#markup-label').disabled=true;const canvas=$('#go-board');canvas.onpointermove=e=>{const p=boardPoint(e.clientX,e.clientY);pointer=p.distance<canvas.getBoundingClientRect().width*.055?{x:p.x,y:p.y,touchPreview:e.pointerType==='touch'}:null;drawBoard()};canvas.onpointerleave=e=>{if(e.pointerType!=='touch'){pointer=null;drawBoard()}};canvas.onpointerdown=e=>{if(e.button!==0)return;const p=boardPoint(e.clientX,e.clientY);if(p.distance>canvas.getBoundingClientRect().width*.055)return;if(addMarkup(p.x,p.y))return;if(e.pointerType==='touch'){const samePoint=touchPreviewAnchor?.x===p.x&&touchPreviewAnchor?.y===p.y;if(!samePoint){touchPreviewAnchor={x:p.x,y:p.y};pointer={x:p.x,y:p.y,touchPreview:true};drawBoard();return}touchPreviewAnchor=null;pointer=null;drawBoard()}try{const ko=last&&!last.pass&&positionHistory.length>1?positionHistory.at(-2):null;const result=applyMove(board,toPlay,p.x,p.y,true,ko);const cap=result.captured.length;appendMove(p.x,p.y);if(cap)playCapture(cap)}catch(err){toast(err.message||tr('illegal'))}};canvas.onkeydown=e=>{if(e.key==='ArrowLeft')previous();if(e.key==='ArrowRight')next(0)};window.addEventListener('resize',()=>{resizeCanvas();refreshTree()});new ResizeObserver(()=>{resizeCanvas();refreshTree()}).observe($('#board-wrap'));
 $('#save-comment').onclick=()=>{updateComment($('#comment').value);toast(tr('commentSaved'))};$('#edit-info').onclick=()=>{for(const [id,key] of [['edit-black','PB'],['edit-white','PW'],['edit-event','EV'],['edit-result','RE'],['edit-komi','KM']])$('#'+id).value=root.props[key]?.[0]||'';$('#info-dialog').showModal()};$('#apply-info').onclick=()=>{for(const [id,key] of [['edit-black','PB'],['edit-white','PW'],['edit-event','EV'],['edit-result','RE'],['edit-komi','KM']])setProp(key,$('#'+id).value.trim());const handicap=Math.max(0,Math.min(9,Number($('#edit-handicap').value)||0));if(path.length>1&&handicap!==Number(root.props.HA?.[0]||0)){toast(tr('handicapBeforeStart'));return}setProp('HA',handicap?String(handicap):'');if(path.length===1){if(handicap)root.props.AB=handicapPoints(boardSize(),handicap);else delete root.props.AB;if(handicap)root.props.PL=['W'];else delete root.props.PL;rebuild();refresh()}toast(tr('metadataSaved'))};$('#library-search').oninput=refreshLibrary;
 $('#font-size').oninput=e=>{$('#font-value').value=`${e.target.value} px`;document.documentElement.style.setProperty('--font',`${e.target.value}px`)};$('#preview-sound').onclick=()=>playSound($('#placement-sound').value);$('#theme').onchange=e=>applyInterfaceTheme(e.target.value);$('#motion').onchange=e=>{prefs.motion=e.target.value;drawBoard()};$('#board-material').onchange=e=>{prefs.board=e.target.value;drawBoard()};$('#stone-material').onchange=e=>{prefs.stones=e.target.value;drawBoard();drawStonePreviews()};$('#save-settings').onclick=()=>{const newSize=Number($('#board-size').value);prefs={...prefs,theme:$('#theme').value,board:$('#board-material').value,stones:$('#stone-material').value,size:newSize,font:Number($('#font-size').value),sound:$('#placement-sound').value,motion:$('#motion').value};if(newSize!==boardSize()){prefs.size=newSize;setupNew(newSize);toast(tr('settingsApplied'))}else{writeStore('ng.preferences',prefs);applyPrefs();toast(tr('settingsApplied'))}};$('#settings-dialog').addEventListener('close',()=>{if($('#settings-dialog').returnValue!=='default')restoreSettings();else{prefs={...prefs,theme:$('#theme').value,board:$('#board-material').value,stones:$('#stone-material').value,font:Number($('#font-size').value),sound:$('#placement-sound').value,motion:$('#motion').value};writeStore('ng.preferences',prefs);applyPrefs()}});
 $('#install-app').onclick=async()=>{if(pendingInstall){pendingInstall.prompt();pendingInstall=null;$('#install-app').hidden=true}};window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();pendingInstall=e;$('#install-app').hidden=false});window.addEventListener('beforeunload',e=>{if(root&&dirty){writeStore('ng.autosave',serializeCollection());e.preventDefault();e.returnValue=''}});
}
function init(){restorePanelOrder();applyLanguage();applyPrefs();drawStonePreviews();bind();bindPanelReordering();const auto=localStorage.getItem('ng.autosave');if(auto){try{const trees=parseSgf(auto);collectionTrees=trees;const tree=trees[0];root=tree;current=root;path=[root];while(current.children?.length){current=current.children[0];path.push(current)}dirty=true}catch{setupNew()}}else setupNew();refresh();refreshModels().then(models=>{const remembered=localStorage.getItem('ng.last-model-id');if(remembered&&models.some(model=>model.id===remembered))loadSelectedModel({automatic:true,id:remembered}).catch(error=>{console.warn('Could not restore the last KataGo model',error);toast(error.message)})}).catch(error=>console.warn('Could not read local models',error));checkGpu();if('serviceWorker'in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('sw.js').catch(()=>{});}
init();
