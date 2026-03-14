import{a as f}from"./config.DbYeYW9v.js";const p={profile:"@components/sidebar/profile.astro",announcement:"@components/sidebar/announcement.astro",categories:"@components/sidebar/categories.astro",tags:"@components/sidebar/tags.astro",toc:"@components/sidebar/toc.astro",statistics:"@components/sidebar/statistics.astro",custom:null};class h{config;constructor(t=f){this.config=t}getConfig(){return this.config}getComponentsBySide(t){return this.config.components[t]||[]}getComponentsByPosition(t){const e=this.getComponentsBySideAndPosition("left",t),n=this.getComponentsBySideAndPosition("right",t);return[...e,...n]}getComponentsBySideAndPosition(t,e){const n=(this.config.components.left||[]).filter(s=>s.position===e),o=(this.config.components.right||[]).filter(s=>s.position===e);return t==="left"?[...n,...o]:t==="right"?o:t==="middle"?[...n,...o]:[]}getComponentClass(t,e,n){const o=[];t.responsive?.hidden&&t.responsive.hidden.forEach(r=>{switch(r){case"mobile":o.push("hidden md:block");break;case"tablet":o.push("md:hidden lg:block");break;case"desktop":o.push("lg:hidden");break}});const s=(this.config.components.left||[]).includes(t),i=(this.config.components.right||[]).includes(t);return n==="left"&&i&&!s&&o.push("hidden md:block lg:hidden"),o.join(" ")}getComponentStyle(t,e){const n=[];return t.style&&n.push(t.style),n.join("; ")}isCollapsed(t,e){return t.responsive?.collapseThreshold?e>=t.responsive.collapseThreshold:!1}getComponentPath(t){return p[t]}hasContentOnSide(t,e=[]){const n=this.getComponentsBySide(t);return n.length===0?!1:n.some(o=>o.type==="toc"?e&&e.length>0:!0)}updateConfig(t){this.config={...this.config,...t}}addComponent(t,e){this.config.components[e]||(this.config.components[e]=[]),this.config.components[e].push(t)}removeComponent(t){this.config.components.left&&(this.config.components.left=this.config.components.left.filter(e=>e.type!==t)),this.config.components.right&&(this.config.components.right=this.config.components.right.filter(e=>e.type!==t))}reorderComponent(t,e,n){const o=this.config.components[t];if(o&&e>=0&&e<o.length&&n>=0&&n<o.length){const[s]=o.splice(e,1);o.splice(n,0,s)}}isSidebarComponent(t){return!0}getPageHeadings(){return typeof document>"u"?[]:Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6")).filter(t=>t.id).map(t=>({depth:parseInt(t.tagName.substring(1)),slug:t.id,text:(t.textContent||"").replace(/#+\s*$/,"")}))}getGridLayout(t=[]){const e=this.hasContentOnSide("left",t),n=this.hasContentOnSide("right",t),o=e||n,s=e,i=n,r=`
            grid-cols-1
            ${o?"md:grid-cols-[17.5rem_1fr]":"md:grid-cols-1"}
            ${s&&i?"lg:grid-cols-[17.5rem_1fr_17.5rem]":s?"lg:grid-cols-[17.5rem_1fr]":i?"lg:grid-cols-[1fr_17.5rem]":"lg:grid-cols-1"}
        `.trim().replace(/\s+/g," "),c=`
            mb-0 col-span-1 hidden
            ${o?"md:block md:max-w-70":""}
            ${s?"lg:block lg:max-w-70 lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-2":"lg:hidden"}
        `.trim().replace(/\s+/g," "),a=`
            mb-0 col-span-1 hidden
            md:hidden
            ${i?s?"lg:block lg:max-w-70 lg:col-start-3 lg:col-end-4 lg:row-start-1 lg:row-end-2":"lg:block lg:max-w-70 lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2":"lg:hidden"}
        `.trim().replace(/\s+/g," "),g=`
            footer col-span-1 onload-animation-up block lg:hidden transition-swup-fade
            ${o?"md:col-span-2":"md:col-span-1"}
        `.trim().replace(/\s+/g," "),d=`
            col-span-1 block md:hidden
            ${o?"":"hidden"}
        `.trim().replace(/\s+/g," "),m=`
            overflow-hidden w-full
            col-span-1 row-start-1 row-end-2
            ${o?"md:col-start-2 md:col-end-3 md:row-start-1 md:row-end-2":"md:col-span-1"}
            ${s&&i||s?"lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2":i?"lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-2":"lg:col-span-1"}
        `.trim().replace(/\s+/g," ");return{hasLeftSidebar:s,hasRightSidebar:i,hasAnyComponents:o,gridCols:r,leftSidebarClass:c,rightSidebarClass:a,mainContentClass:m,mobileFooterClass:g,middleSidebarClass:d}}}const C=new h;function b(l,t,e,n){if(typeof document>"u")return;const o=document.getElementById(t),s=l.target,i=Array.isArray(e)?e:[e];for(const r of i)if(s.closest(`#${r}`))return;o&&!o.contains(s)&&n()}export{b as o,C as w};
