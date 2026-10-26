<script setup>
import { computed, h } from "vue";
import { parseRichText } from "../utils/richText";

const props = defineProps({
  text: { type: String, default: "" },
});

const segments = computed(() => parseRichText(props.text));

function renderSegment(segment) {
  let node = segment.text;
  if (segment.bold) node = h("strong", node);
  if (segment.italic) node = h("i", node);
  if (segment.italian) node = h("span", { lang: "it" }, node);
  return node;
}

const render = () => h("span", segments.value.map(renderSegment));
</script>

<template>
  <render />
</template>
