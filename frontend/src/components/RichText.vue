<template>
  <span
    ><template v-for="(seg, i) in segments" :key="i"
      ><i v-if="seg.tag === 'i'">{{ seg.text }}</i
      ><strong v-else-if="seg.tag === 'strong'">{{ seg.text }}</strong
      ><template v-else>{{ seg.text }}</template></template
    ></span
  >
</template>

<script setup>
import { computed } from "vue";

const INLINE_TAGS = /(<\/?(?:i|strong)>)/g;

const props = defineProps({
  text: { type: String, default: "" },
});

const segments = computed(() => {
  const parts = props.text.split(INLINE_TAGS).filter((part) => part !== "");
  const segments = [];
  let tag = null;
  for (const part of parts) {
    if (part === "<i>") tag = "i";
    else if (part === "<strong>") tag = "strong";
    else if (part === "</i>" || part === "</strong>") tag = null;
    else segments.push({ tag, text: part });
  }
  return segments;
});
</script>
