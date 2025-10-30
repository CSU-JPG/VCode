// =======================================================
// MM-VET CONFIGURATION
// =======================================================
const DATA_JSON = 'mm-vet/mm-vet.json';
const METHOD_SETS = {
  'img2svg': 'Img2SVG', 
  'img2text2svg': 'Img2Text2SVG', 
  'img2svg-thinking': 'Img2SVG-Thinking',
  'img2svg-revision': 'Img2SVG-Revision',
  'img2svg-revision-text': 'Img2SVG-Revision-Text',
  'img2svg-gsam': 'Img2SVG+Location&Category&Shape',
  'img2svg-hint': 'Img2SVG-Hint',
  'img2svg-hint-revision': 'Img2SVG-Hint-Revision',
  'img2svg-ocr': 'Img2SVG+Text',
  'img2svg-florence': 'Img2SVG+Location&Category',
  'img2svg-all-in-one-revision': 'Img2SVG+VCoder',
};

const GENERATOR_SETS = {
  'cla': 'Claude-4-Opus', 
  'claS': 'Claude-4-Sonnet', 
  'gem': 'Gemini-2.5-Pro',
  'gemf': 'Gemini-2.5-Flash',
  'qwn': 'Qwen2.5-VL-72B', 
  'gpt': 'GPT-4o', 
  'gpt4.1': 'GPT4.1',
  'g4omni': 'GPT-4o-mini',
  'internvl3': 'InternVL3-78B',
  'seed1.6': 'Seed-1.6-Thinking',
  'gpt5': 'GPT-5',
  'cla4.5S': 'Claude-4.5-Sonnet',
  'glm4.1Vthink': 'GLM-4.1V-Thinking',
  'glm4.5V': 'GLM-4.5V',
  'gpto3': 'GPT-o3',
  'interns1': 'Intern-S1',
  'internvl3.5': 'InternVL3.5',
  'llama4': 'Llama-4',
  'minicpmv4.5': 'MiniCPM-V-4.5',
  'omnisvg': 'OmniSVG',
  'qwen2.5vl7b': 'Qwen2.5-VL-7B',
  'qwen3vl': 'Qwen3-VL',
  'starvector': 'StarVector',
  'vcoder': 'VCoder',
};

const GENERATOR_VARIANTS = {
  'cla': ['cla', 'clatxt', 'clathink','claRev','claRevtxt','clagsam', 'clahint', 'clahintRev', 'claocr','claflorence', 'vcoder'], 
  'claS': ['claS', 'claStxt', 'claSthink'],
  'cla4.5S': ['cla4.5S'],
  'gemf': ['gemf'],
  'gem': ['gem'], 
  'qwn': ['qwn'],
  'glm4.5V': ['glm4.5V'],
  'glm4.1Vthink': ['glm4.1Vthink'],
  'interns1': ['interns1'],
  'internvl3.5': ['internvl3.5'],
  'internvl3': ['internvl3'],
  'seed1.6': ['seed1.6', 'seed1.6txt'],
  'llama4': ['llama4'],
  'minicpmv4.5': ['minicpmv4.5'],
  'omnisvg': ['omnisvg'],
  'qwen2.5vl7b': 'Qwen2.5-VL-7B',
  'qwen3vl': 'Qwen3-VL',
  'starvector': ['starvector'],
  'vcoder': ['vcoder'],
  'gpt': ['gpt', 'gpttxt'], 
  'gpto3': ['gpto3'],
  'gpt5': ['gpt5', 'gpt5txt'],
  'gpt4.1': ['gpt4.1', 'gpt4.1txt'],
  'g4omni': ['g4omni', 'g4omnitxt']
};

const TEXT_SET = {
    'clatxt': 'mm-vet/text/claude_from_text.json',
    'clathink': 'mm-vet/text/claude_thinking.json',
    'claStxt': 'mm-vet/text/claude_sonnet_from_text.json',
    'claSthink': 'mm-vet/text/claude_sonnet_thinking.json',
    'gpt4.1txt': 'mm-vet/text/gpt4.1_from_text.json',
    'g4omnitxt': 'mm-vet/text/gpt4o_mini_from_text.json',
    'gpttxt': 'mm-vet/text/gpt4o_from_text.json',
    'seed1.6txt': 'mm-vet/text/seed1.6_from_text.json',
    'gpt5txt': 'mm-vet/text/gpt5_from_text.json',
};

const PRED_SET   = {
  '7B': {orig:'mm-vet/prediction/qwen7b/pred_original.json', cla:'mm-vet/prediction/qwen7b/pred_claude.json', gem:'mm-vet/prediction/qwen7b/pred_gemini.json', qwn:'mm-vet/prediction/qwen7b/pred_qwen.json', gpt:'mm-vet/prediction/qwen7b/pred_gpt.json'},
  '3B': {orig:'mm-vet/prediction/qwen3b/pred_original.json', cla:'mm-vet/prediction/qwen3b/pred_claude.json', gem:'mm-vet/prediction/qwen3b/pred_gemini.json', qwn:'mm-vet/prediction/qwen3b/pred_qwen.json', gpt:'mm-vet/prediction/qwen3b/pred_gpt.json'},
  'g4omini': {
    orig:'mm-vet/prediction/gpt4o-mini/pred_original.json', 
    cla:'mm-vet/prediction/gpt4o-mini/pred_claude.json', 
    clatxt:'mm-vet/prediction/gpt4o-mini/pred_claude_from_text.json', 
    gem:'mm-vet/prediction/gpt4o-mini/pred_gemini.json', 
    qwn:'mm-vet/prediction/gpt4o-mini/pred_qwen.json', 
    gpt:'mm-vet/prediction/gpt4o-mini/pred_gpt.json', 
    'gpt4.1':'mm-vet/prediction/gpt4o-mini/pred_gpt4.1.json', 
    'gpt4.1txt': 'mm-vet/prediction/gpt4o-mini/pred_gpt4.1_from_text.json',
    'claS':'mm-vet/prediction/gpt4o-mini/pred_claSonnet.json',
    'claStxt':'mm-vet/prediction/gpt4o-mini/pred_claSonnet_from_text.json',
    'claSthink':'mm-vet/prediction/gpt4o-mini/pred_claSonnet_thinking.json',
    'g4omni':'mm-vet/prediction/gpt4o-mini/pred_g4omini.json',
    'g4omnitxt':'mm-vet/prediction/gpt4o-mini/pred_g4omini_from_text.json',
    'clathink':'mm-vet/prediction/gpt4o-mini/pred_claude_thinking.json',
    'internvl3':'mm-vet/prediction/gpt4o-mini/pred_internvl3.json',
    'gpttxt': 'mm-vet/prediction/gpt4o-mini/pred_gpt_from_text.json',
    'seed1.6': 'mm-vet/prediction/gpt4o-mini/pred_seed1.6.json',
    'seed1.6txt': 'mm-vet/prediction/gpt4o-mini/pred_seed1.6_from_text.json',
    'claRev': 'mm-vet/prediction/gpt4o-mini/pred_claude_revision.json',
    'claRevtxt': 'mm-vet/prediction/gpt4o-mini/pred_claude_revision_from_text.json',
    'clagsam': 'mm-vet/prediction/gpt4o-mini/pred_claude_gsam.json',
    'clahint': 'mm-vet/prediction/gpt4o-mini/pred_claude_hint.json',
    'clahintRev': 'mm-vet/prediction/gpt4o-mini/pred_claude_hint_revision.json',
    'claocr': 'mm-vet/prediction/gpt4o-mini/pred_claude_ocr.json',
    'gpt5': 'mm-vet/prediction/gpt4o-mini/pred_gpt5.json',
    'gpt5txt': 'mm-vet/prediction/gpt4o-mini/pred_gpt5_from_text.json',
    'claflorence': 'mm-vet/prediction/gpt4o-mini/pred_claude_florence.json',
    // new
    'gemf': 'mm-vet/prediction/gpt4o-mini/pred_gemini_2.5_flash.json',
    'cla4.5S': 'mm-vet/prediction/gpt4o-mini/pred_claude_4.5_sonnet.json',
    'glm4.1Vthink': 'mm-vet/prediction/gpt4o-mini/pred_glm4.1v_thinking.json',
    'glm4.5V': 'mm-vet/prediction/gpt4o-mini/pred_glm4.5v.json',
    'gpto3': 'mm-vet/prediction/gpt4o-mini/pred_gpt_o3.json',
    'interns1': 'mm-vet/prediction/gpt4o-mini/pred_interns1.json',
    'internvl3.5': 'mm-vet/prediction/gpt4o-mini/pred_internvl3.5.json',
    'llama4': 'mm-vet/prediction/gpt4o-mini/pred_llama4.json',
    'minicpmv4.5': 'mm-vet/prediction/gpt4o-mini/pred_minicpmv4.5.json',
    'omnisvg': 'mm-vet/prediction/gpt4o-mini/pred_omnisvg.json',
    'qwen2.5vl7b': 'mm-vet/prediction/gpt4o-mini/pred_qwen2.5vl7b.json',
    'qwen3vl': 'mm-vet/prediction/gpt4o-mini/pred_qwen3vl.json',
    'starvector': 'mm-vet/prediction/gpt4o-mini/pred_starvector.json',
    'vcoder': 'mm-vet/prediction/gpt4o-mini/pred_vcoder.json',
  }
};
const SCORE_SET  = {
  '7B': {orig:'mm-vet/score/qwen7b/score_original.json', cla:'mm-vet/score/qwen7b/score_claude.json', gem:'mm-vet/score/qwen7b/score_gemini.json', qwn:'mm-vet/score/qwen7b/score_qwen.json', gpt:'mm-vet/score/qwen7b/score_gpt.json'},
  '3B': {orig:'mm-vet/score/qwen3b/score_original.json', cla:'mm-vet/score/qwen3b/score_claude.json', gem:'mm-vet/score/qwen3b/score_gemini.json', qwn:'mm-vet/score/qwen3b/score_qwen.json', gpt:'mm-vet/score/qwen3b/score_gpt.json'},
  'g4omini': {
    orig:'mm-vet/score/gpt4o-mini/score_original.json',
    cla:'mm-vet/score/gpt4o-mini/score_claude.json',
    clatxt:'mm-vet/score/gpt4o-mini/score_claude_from_text.json', 
    gem:'mm-vet/score/gpt4o-mini/score_gemini.json', 
    qwn:'mm-vet/score/gpt4o-mini/score_qwen.json', 
    gpt:'mm-vet/score/gpt4o-mini/score_gpt.json', 
    'gpt4.1':'mm-vet/score/gpt4o-mini/score_gpt4.1.json', 
    'gpt4.1txt': 'mm-vet/score/gpt4o-mini/score_gpt4.1_from_text.json',
    'claS':'mm-vet/score/gpt4o-mini/score_claSonnet.json',
    'claStxt':'mm-vet/score/gpt4o-mini/score_claSonnet_from_text.json',
    'claSthink':'mm-vet/score/gpt4o-mini/score_claSonnet_thinking.json',
    'g4omni':'mm-vet/score/gpt4o-mini/score_g4omini.json',
    'g4omnitxt':'mm-vet/score/gpt4o-mini/score_g4omini_from_text.json',
    'clathink':'mm-vet/score/gpt4o-mini/score_claude_thinking.json',
    'internvl3':'mm-vet/score/gpt4o-mini/score_internvl3.json',
    'gpttxt': 'mm-vet/score/gpt4o-mini/score_gpt_from_text.json',
    'seed1.6': 'mm-vet/score/gpt4o-mini/score_seed1.6.json',
    'seed1.6txt': 'mm-vet/score/gpt4o-mini/score_seed1.6_from_text.json',
    'claRev': 'mm-vet/score/gpt4o-mini/score_claude_revision.json',
    'claRevtxt': 'mm-vet/score/gpt4o-mini/score_claude_revision_from_text.json',
    'clagsam': 'mm-vet/score/gpt4o-mini/score_claude_gsam.json',
    'clahint': 'mm-vet/score/gpt4o-mini/score_claude_hint.json',
    'clahintRev': 'mm-vet/score/gpt4o-mini/score_claude_hint_revision.json',
    'claocr': 'mm-vet/score/gpt4o-mini/score_claude_ocr.json',
    'gpt5': 'mm-vet/score/gpt4o-mini/score_gpt5.json',
    'gpt5txt': 'mm-vet/score/gpt4o-mini/score_gpt5_from_text.json',
    'claflorence': 'mm-vet/score/gpt4o-mini/score_claude_florence.json',
    // new
    'gemf': 'mm-vet/score/gpt4o-mini/score_gemini_2.5_flash.json',
    'cla4.5S': 'mm-vet/score/gpt4o-mini/score_claude_4.5_sonnet.json',
    'glm4.1Vthink': 'mm-vet/score/gpt4o-mini/score_glm4.1v_think.json',
    'glm4.5V': 'mm-vet/score/gpt4o-mini/score_glm4.5v.json',
    'gpto3': 'mm-vet/score/gpt4o-mini/score_gpt-o3.json',
    'interns1': 'mm-vet/score/gpt4o-mini/score_interns1.json',
    'internvl3.5': 'mm-vet/score/gpt4o-mini/score_internvl3.5.json',
    'llama4': 'mm-vet/score/gpt4o-mini/score_llama4.json',
    'minicpmv4.5': 'mm-vet/score/gpt4o-mini/score_minicpmv4.5.json',
    'omnisvg': 'mm-vet/score/gpt4o-mini/score_omnisvg.json',
    'qwen2.5vl7b': 'mm-vet/score/gpt4o-mini/score_qwen2.5vl7b.json',
    'qwen3vl': 'mm-vet/score/gpt4o-mini/score_qwen3vl.json',
    'starvector': 'mm-vet/score/gpt4o-mini/score_starvector.json',
    'vcoder': 'mm-vet/score/gpt4o-mini/score_vcoder.json',
  }
};
const IMG_DIR = {
  orig:'mm-vet/images/', 
  cla:'mm-vet/images_claude/',
  clatxt:'mm-vet/images_claude_from_text/', 
  gem:'mm-vet/images_gemini/', 
  qwn:'mm-vet/images_qwen/', 
  gpt:'mm-vet/images_gpt/', 
  'gpt4.1':'mm-vet/images_gpt4.1/', 
  'gpt4.1txt': 'mm-vet/images_gpt4.1_from_text/',
  'claS':'mm-vet/images_claude_sonnet/',
  'claStxt':'mm-vet/images_claude_sonnet_from_text/',
  'claSthink':'mm-vet/images_claude_sonnet_thinking/',
  'g4omni':'mm-vet/images_g4omini/',
  'g4omnitxt':'mm-vet/images_g4omini_from_text/',
  'clathink':'mm-vet/images_claude_thinking/',
  'internvl3':'mm-vet/images_internvl3/',
  'gpttxt': 'mm-vet/images_gpt_from_text/',
  'seed1.6': 'mm-vet/images_seed1.6/',
  'seed1.6txt': 'mm-vet/images_seed1.6_from_text/',
  'claRev': 'mm-vet/images_claude_revision/',
  'claRevtxt': 'mm-vet/images_claude_revision_from_text/',
  'clagsam': 'mm-vet/images_claude_gsam/',
  'clahint': 'mm-vet/images_claude_hint/',
  'clahintRev': 'mm-vet/images_claude_hint_revision/',
  'claocr': 'mm-vet/images_claude_ocr/',
  'gpt5': 'mm-vet/images_gpt5/',
  'gpt5txt': 'mm-vet/images_gpt5_from_text/',
  'claflorence': 'mm-vet/images_claude_florence/',
  // new
  'gemf': 'mm-vet/images_gemini_2.5_flash/',
  'cla4.5S': 'mm-vet/images_claude_4.5_sonnet/',
  'glm4.1Vthink': 'mm-vet/images_glm4.1v_think/',
  'glm4.5V': 'mm-vet/images_glm4.5v/',
  'gpto3': 'mm-vet/images_gpto3/',
  'interns1': 'mm-vet/images_interns1/',
  'internvl3.5': 'mm-vet/images_internvl3.5/',
  'llama4': 'mm-vet/images_llama4/',
  'minicpmv4.5': 'mm-vet/images_minicpmv4.5/',
  'omnisvg': 'mm-vet/images_omnisvg/',
  'qwen2.5vl7b': 'mm-vet/images_qwen2.5vl7b/',
  'qwen3vl': 'mm-vet/images_qwen3vl/',
  'starvector': 'mm-vet/images_starvector/',
  'vcoder': 'mm-vet/images_vcoder/',
};

const renderConfig = {
    variantsByMethod: { 'img2svg': ['cla', 'gem', 'qwn', 'gpt', 'gpt4.1', 'claS', 'g4omni', 'internvl3', 'seed1.6', 'gpt5', 'gemf','cla4.5S', 'glm4.1Vthink', 'glm4.5V', 'gpto3', 'interns1', 'internvl3.5', 'llama4', 'minicpmv4.5', 'omnisvg', 'qwen2.5vl7b', 'qwen3vl', 'starvector', 'vcoder'], 'img2text2svg': ['clatxt', 'gpt4.1txt', 'claStxt', 'g4omnitxt', 'gpttxt', 'seed1.6txt', 'gpt5txt'], 'img2svg-thinking': ['clathink', 'claSthink'], 'img2svg-revision': ['claRev'], 'img2svg-revision-text': ['claRevtxt'], 'img2svg-gsam': ['clagsam'], 'img2svg-hint': ['clahint'], 'img2svg-hint-revision': ['clahintRev'], 'img2svg-ocr': ['claocr'], 'img2svg-florence': ['claflorence'], 'img2svg-all-in-one-revision':['vcoder'] },
  headerLabels: {
    orig: 'Orig. Image', cla: 'Claude-4-Opus', gemf: 'Gemini-2.5-Flash', 'cla4.5S': 'Claude-4.5-Sonnet', 'glm4.1Vthink': 'GLM-4.1-Thinking', 'glm4.5V': 'GLM-4.5V', gpto3: 'GPT-o3', interns1: 'Intern-S1', 'internvl3.5': 'InternVL-3.5', llama4: 'Llama-4', 'minicpmv4.5': 'MiniCPM-V-4.5', omnisvg: 'OmniSVG', 'qwen2.5vl7b': 'Qwen2.5-VL-7B', qwen3vl: 'Qwen3-VL', starvector: 'StarVector', vcoder: 'VCoder',
    clatxt: 'Claude-4-Opus-Txt', gem: 'Gemini-2.5-Pro', qwn: 'Qwen2.5-VL-72B', gpt: 'GPT-4o', 'gpttxt': 'GPT-4o-Txt', 'gpt4.1': 'GPT-4.1', 'gpt4.1txt': 'GPT-4.1-Txt', 'claS': 'Claude-4-Sonnet', 'claStxt': 'Claude-4-Sonnet-Txt', 'claSthink': 'Claude-4-Sonnet-Th', 'g4omni': 'GPT-4o-mini', 'g4omnitxt': 'GPT-4o-mini-Txt', 'clathink': 'Claude-4-Opus-Th', 'internvl3': 'InternVL3', 'seed1.6': 'Seed1.6', 'seed1.6txt': 'Seed1.6-Txt', 'claRev': 'Claude-4-Opus-Rev', 'claRevtxt': 'Claude-4-Opus-Rev-Txt', 'clagsam': 'Claude-4-Opus+L&C&S', 'clahint': 'Claude-4-Opus-Hint', 'clahintRev': 'Claude-4-Opus-Hint-Rev', 'claocr': 'Claude-4-Opus+Txt', 'gpt5': 'GPT-5', 'gpt5txt': 'GPT-5-Txt', 'claflorence': 'Claude-4-Opus+L&C', 'vcoder': 'Claude-4-Opus+VCoder'
  },
    scoreLabels: { orig: 'S-Orig', cla: 'S-Cla', clatxt: 'S-ClaT', gem: 'S-Gem', qwn: 'S-Qwn', gpt: 'S-GPT', 'gpttxt': 'S-GPT-Txt', 'gpt4.1': 'S-GPT4.1', 'gpt4.1txt': 'S-GPT4.1T', 'claS': 'S-ClaS', 'claStxt': 'S-ClaST', 'claSthink': 'S-ClaSTh', 'g4omni': 'S-G4o-mini', 'g4omnitxt': 'S-G4ominiT', 'clathink': 'S-Cla-Th', 'internvl3': 'S-InternVL3', 'seed1.6': 'S-Seed', 'seed1.6txt': 'S-SeedT', 'claRev': 'S-ClaR', 'claRevtxt': 'S-ClaRev-Txt', 'clagsam': 'S-ClaGSAM', 'clahint': 'S-ClaHint', 'clahintRev': 'S-ClaHintR', 'claocr': 'S-ClaOCR', 'gpt5': 'S-GPT5', 'gpt5txt': 'S-GPT5-Txt', 'claflorence': 'S-ClaFlorence' }
};

// =======================================================
// CV-BENCH CONFIGURATION
// =======================================================

const CVBENCH_CONFIG = {
    inferenceModels: {
        'g4omini': 'GPT-4o-mini'
    },
    origConfig: {
        name: 'cv-bench/Orig',
        files: [
            'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
            'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
            'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
        ]
    },
    capabilities: {
        "spatial": "Spatial Relationship",
        "count": "Object Count",
        "depth": "Depth Order",
        "relative": "Relative Distance"
    },
generators: {
  'cla': {
    name: 'cv-bench/Claude-4-Opus',
    label: 'Claude-4-Opus',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'clason45': {
    name: 'cv-bench/Claude-4.5-Sonnet',
    label: 'Claude-4.5-Sonnet',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'clason': {
    name: 'cv-bench/Claude-4-Sonnet',
    label: 'Claude-4-Sonnet',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g25f': {
    name: 'cv-bench/Gemini-2.5-Flash',
    label: 'Gemini-2.5-Flash',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g25p': {
    name: 'cv-bench/Gemini-2.5-Pro',
    label: 'Gemini-2.5-Pro',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'glm41vt': {
    name: 'cv-bench/GLM-4.1V-Thinking',
    label: 'GLM-4.1V-Thinking',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'glm45v': {
    name: 'cv-bench/GLM-4.5V',
    label: 'GLM-4.5V',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g41': {
    name: 'cv-bench/GPT-4.1',
    label: 'GPT-4.1',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g4o': {
    name: 'cv-bench/GPT-4o',
    label: 'GPT-4o',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g4om': {
    name: 'cv-bench/GPT-4o-mini',
    label: 'GPT-4o-mini',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'g5': {
    name: 'cv-bench/GPT-5',
    label: 'GPT-5',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'go3': {
    name: 'cv-bench/GPT-o3',
    label: 'GPT-o3',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'llama4': {
    name: 'cv-bench/Llama-4',
    label: 'Llama-4-Scout-17B-16E-Instruct',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  's1': {
    name: 'cv-bench/Intern-S1',
    label: 'Intern-S1',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'ivl35': {
    name: 'cv-bench/InternVL3.5',
    label: 'InternVL3.5',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'ivl78': {
    name: 'cv-bench/InternVL3-78B',
    label: 'InternVL3-78B',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'mcp45': {
    name: 'cv-bench/MiniCPM-V-4.5',
    label: 'MiniCPM-V-4.5',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'qv3vl': {
    name: 'cv-bench/Qwen3-VL',
    label: 'Qwen3-VL-235B-A22B-Instruct',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'qv7b': {
    name: 'cv-bench/Qwen2.5-VL-7B',
    label: 'Qwen2.5-VL-7B',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'qv72b': {
    name: 'cv-bench/Qwen2.5-VL-72B',
    label: 'Qwen2.5-VL-72B',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'seed16t': {
    name: 'cv-bench/Seed-1.6-Thinking',
    label: 'Seed-1.6-Thinking',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'omnisvg': {
    name: 'cv-bench/OmniSVG',
    label: 'OmniSVG',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'sv8b': {
    name: 'cv-bench/StarVector-8B',
    label: 'StarVector-8B',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  },
  'vcode': {
    name: 'cv-bench/VCoder',
    label: 'VCoder',
    files: [
      'gpt-4o-mini-2024-07-18_answers_ade.jsonl',
      'gpt-4o-mini-2024-07-18_answers_coco.jsonl',
      'gpt-4o-mini-2024-07-18_answers_omni.jsonl'
    ]
  }
},

methodSets: {
  'img2svg': 'Img2SVG'
},

renderConfig: {
  variantsByMethod: {
    'img2svg': [ 'cla','clason45','clason','g25f','g25p','glm41vt','glm45v','g41','g4o','g4om','g5','go3','llama4','s1','ivl35','ivl78', 'mcp45','qv3vl','qv7b','qv72b','seed16t','omnisvg','sv8b','vcode'
    ]
  },
  headerLabels: {
    'orig': 'Orig. Image',
    'cla': 'Claude-4-Opus',
    'clason45': 'Claude-4.5-Sonnet',
    'clason': 'Claude-4-Sonnet',
    'g25f': 'Gemini-2.5-Flash',
    'g25p': 'Gemini-2.5-Pro',
    'glm41vt': 'GLM-4.1V-Th',
    'glm45v': 'GLM-4.5V',
    'g41': 'GPT-4.1',
    'g4o': 'GPT-4o',
    'g4om': 'GPT-4o-mini',
    'g5': 'GPT-5',
    'go3': 'GPT-o3',
    'llama4': 'Llama-4',
    's1': 'Intern-S1',
    'ivl35': 'InternVL3.5',
    'ivl78': 'InternVL3-78B',
    'mcp45': 'MiniCPM-V-4.5',
    'qv3vl': 'Qwen3-VL',
    'qv7b': 'Qwen2.5-VL-7B',
    'qv72b': 'Qwen2.5-VL-72B',
    'seed16t': 'Seed-1.6-Th',
    'omnisvg': 'OmniSVG-3B',
    'sv8b': 'StarVector-8B',
    'vcode': 'VCoder'
  },
  scoreLabels: {
    'orig': 'S-Orig',
    'cla': 'S-Cla',
    'clason45': 'S-Clason45',
    'clason': 'S-Clason',
    'g25f': 'S-G2.5F',
    'g25p': 'S-G2.5P',
    'glm41vt': 'S-GLM41VTh',
    'glm45v': 'S-GLM45V',
    'g41': 'S-G4.1',
    'g4o': 'S-G4o',
    'g4om': 'S-G4oM',
    'g5': 'S-G5',
    'go3': 'S-Go3',
    'llama4': 'S-Llama4',
    's1': 'S-InternS1',
    'ivl35': 'S-IVL3.5',
    'ivl78': 'S-IVL78B',
    'mcp45': 'S-MiniCPM45',
    'qv3vl': 'S-Qwen3VL',
    'qv7b': 'S-Qwen7B',
    'qv72b': 'S-Qwen72B',
    'seed16t': 'S-Seed16Th',
    'omnisvg': 'S-OmniSVG',
    'sv8b': 'S-StarVector8B',
    'vcode': 'S-VCoder'
  }
}

};

// =======================================================
// MMMU CONFIGURATION
// =======================================================

const MMMU_CONFIG = {
    questionFile: 'mmmu/questions.json',
    
    subtasks: [
        'Accounting',
        'Agriculture',
        'Architecture_and_Engineering',
        'Art',
        'Art_Theory',
        'Basic_Medical_Science',
        'Biology',
        'Chemistry',
        'Clinical_Medicine',
        'Computer_Science',
        'Design',
        'Diagnostics_and_Laboratory_Medicine',
        'Economics',
        'Electronics',
        'Energy_and_Power',
        'Finance',
        'Geography',
        'History',
        'Literature',
        'Manage',
        'Marketing',
        'Materials',
        'Math',
        'Mechanical_Engineering',
        'Music',
        'Pharmacy',
        'Physics',
        'Psychology',
        'Public_Health',
        'Sociology'
    ],

    origConfig: {
        name: 'mmmu/Orig',
    },
    inferenceModels: {
        'g4omini': 'GPT-4o-mini'
    },
    
    generators: {
      'cla': { name: 'mmmu/Claude-4-Opus', label: 'Claude-4-Opus' },
      'cla_son45': { name: 'mmmu/Claude-4.5-Sonnet', label: 'Claude-4.5-Sonnet' },
      'cla_son':  { name: 'mmmu/Claude-4-Sonnet', label: 'Claude-4-Sonnet' },
      'gem25f':   { name: 'mmmu/Gemini-2.5-Flash', label: 'Gemini-2.5-Flash' },
      'gem25p':   { name: 'mmmu/Gemini-2.5-Pro', label: 'Gemini-2.5-Pro' },
      'glm41vt':  { name: 'mmmu/GLM-4.1V-Thinking', label: 'GLM-4.1V-Thinking' },
      'glm45v':   { name: 'mmmu/GLM-4.5V', label: 'GLM-4.5V' },
      'g41':      { name: 'mmmu/GPT-4.1', label: 'GPT-4.1' },
      'g4o':      { name: 'mmmu/GPT-4o', label: 'GPT-4o' },
      'g4omini':  { name: 'mmmu/GPT-4o-mini', label: 'GPT-4o-mini' },
      'g5':       { name: 'mmmu/GPT-5', label: 'GPT-5' },
      'go3': { name: 'mmmu/GPT-o3', label: 'GPT-o3' },
      'llama4': { name: 'mmmu/Llama-4', label: 'Llama-4' },
      'interns1': { name: 'mmmu/Intern-S1', label: 'Intern-S1' },
      'ivl35':    { name: 'mmmu/InternVL3.5', label: 'InternVL3.5' },
      'ivl3_78b': { name: 'mmmu/InternVL3-78B', label: 'InternVL3-78B' },
      'minicpm': { name: 'mmmu/MiniCPM-V-4_5', label: 'MiniCPM-V-4_5' },
      'omnisvg': { name: 'mmmu/OmniSVG', label: 'OmniSVG' },
      'qwen3vl': { name: 'mmmu/Qwen3-VL', label: 'Qwen3-VL' },
      'qwen7b':   { name: 'mmmu/Qwen2.5-VL-7B', label: 'Qwen2.5-VL-7B' },
      'qwen72b':  { name: 'mmmu/Qwen2.5-VL-72B', label: 'Qwen2.5-VL-72B' },
      'seed16t':  { name: 'mmmu/Seed-1.6-Thinking', label: 'Seed-1.6-Thinking' },
      'starvec': { name: 'mmmu/StarVector', label: 'StarVector' },
      'vcoderc':  { name: 'mmmu/VCoder', label: 'VCoder' },
    },
    methodSets: {
        'img2svg': 'Img2SVG'
    },
    renderConfig: {
       variantsByMethod: {
        'img2svg': [
        'cla','cla_son45','cla_son','gem25f','gem25p','glm41vt','glm45v',
        'g41','g4o','g4omini','g5','go3','llama4',
        'interns1','ivl35','ivl3_78b','minicpm',
        'omnisvg','qwen3vl','qwen7b','qwen72b','seed16t','starvec','vcoderc']
       },
    headerLabels: {
      'orig': 'Orig. Image',
      'cla':'Claude-4-Opus','cla_son45':'Claude-4.5-Sonnet','cla_son':'Claude-4-Sonnet',
      'gem25f':'Gemini-2.5-Flash','gem25p':'Gemini-2.5-Pro',
      'glm41vt':'GLM-4.1V-Thinking','glm45v':'GLM-4.5V',
      'g41':'GPT-4.1','g4o':'GPT-4o','g4omini':'GPT-4o-mini','g5':'GPT-5','go3':'GPT-o3','llama4':'Llama-4',
      'interns1':'Intern-S1','ivl35':'InternVL3.5','ivl3_78b':'InternVL3-78B',
      'minicpm':'MiniCPM-V-4_5','omnisvg':'OmniSVG-3B','qwen3vl':'Qwen3-VL','qwen7b':'Qwen2.5-VL-7B','qwen72b':'Qwen2.5-VL-72B',
      'seed16t':'Seed-1.6-Thinking','starvec':'StarVector-8B','vcoderc':'VCoder'
    },
    scoreLabels: {
      'orig':'S-Orig',
      'cla':'S-Cla-Opus','cla_son45':'S-Cla-Sonnet4.5','cla_son':'S-Cla-Sonnet',
      'gem25f':'S-Gem-2.5F','gem25p':'S-Gem-2.5P',
      'glm41vt':'S-GLM-4.1V-T','glm45v':'S-GLM-4.5V',
      'g41':'S-GPT-4.1','g4o':'S-GPT-4o','g4omini':'S-GPT-4o-mini','g5':'S-GPT-5','go3':'S-GPT-o3','llama4':'S-Llama4',
      'interns1':'S-Intern-S1','ivl35':'S-InternVL3.5','ivl3_78b':'S-InternVL3-78B',
      'minicpm':'S-MiniCPM-V-4_5','omnisvg':'S-OmniSVG','qwen3vl':'S-Qwen3VL','qwen7b':'S-Qwen2.5-VL-7B','qwen72b':'S-Qwen2.5-VL-72B',
      'seed16t':'S-Seed-1.6-T','starvec':'S-StarVector','vcoderc':'S-VCoder',
    }
  }
};