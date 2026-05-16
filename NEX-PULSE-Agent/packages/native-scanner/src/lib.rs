use std::ffi::{CStr, CString};
use std::os::raw::c_char;

// Función expuesta a C/Python para escaneo rápido
#[no_mangle]
pub extern "C" fn scan_mft_for_junk(target_drive: *const c_char) -> *mut c_char {
    let drive = unsafe { 
        if target_drive.is_null() {
            "C:".to_string()
        } else {
            CStr::from_ptr(target_drive).to_string_lossy().into_owned() 
        }
    };
    
    // Simulación de lectura ultrarrápida (Placeholder para MFT parsing)
    // Aquí es donde irá la lógica interactuando con fsutil o winapi
    let result = format!(r#"{{"drive": "{}", "scanned_files": 1542000, "junk_found_mb": 4500, "status": "success"}}"#, drive);
    
    CString::new(result).unwrap().into_raw()
}

// Es crítico que Python llame esto para evitar Memory Leaks
#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if s.is_null() { return; }
    unsafe {
        let _ = CString::from_raw(s);
    }
}
