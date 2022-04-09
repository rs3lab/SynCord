__kpatch_funcs = ADDR(.kpatch.funcs);
__kpatch_funcs_end = ADDR(.kpatch.funcs) + SIZEOF(.kpatch.funcs);
SECTIONS
{
  .kpatch.callbacks.pre_patch : {
    __kpatch_callbacks_pre_patch = . ;
    *(.kpatch.callbacks.pre_patch)
    __kpatch_callbacks_pre_patch_end = . ;
    QUAD(0);
  }
  .kpatch.callbacks.post_patch : {
    __kpatch_callbacks_post_patch = . ;
    *(.kpatch.callbacks.post_patch)
    __kpatch_callbacks_post_patch_end = . ;
    QUAD(0);
  }
  .kpatch.callbacks.pre_unpatch : {
    __kpatch_callbacks_pre_unpatch = . ;
    *(.kpatch.callbacks.pre_unpatch)
    __kpatch_callbacks_pre_unpatch_end = . ;
    QUAD(0);
  }
  .kpatch.callbacks.post_unpatch : {
    __kpatch_callbacks_post_unpatch = . ;
    *(.kpatch.callbacks.post_unpatch)
    __kpatch_callbacks_post_unpatch_end = . ;
    QUAD(0);
  }
  .kpatch.force : {
    __kpatch_force_funcs = . ;
    *(.kpatch.force)
    __kpatch_force_funcs_end = . ;
    QUAD(0);
  }
}
