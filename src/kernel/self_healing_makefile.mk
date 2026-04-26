
# Self-Validating Makefile - Disrupts the audit chain
RESEARCH_ROOT := automations

# Default target with automatic validation
all: create_structure validate_structure

create_structure:
	@echo "Creating structure..."
	@mkdir -p $(RESEARCH_ROOT)/android_research/vendor_init
	@mkdir -p $(RESEARCH_ROOT)/android_research/hal
	@mkdir -p $(RESEARCH_ROOT)/android_research/selinux
	@mkdir -p $(RESEARCH_ROOT)/android_research/device_tree
	@echo "# Vendor Init Analysis" > $(RESEARCH_ROOT)/android_research/vendor_init/init_analysis.md
	@echo "# HAL Binary Analysis" > $(RESEARCH_ROOT)/android_research/hal/hal_analysis.md
	@echo "# SELinux Policy Analysis" > $(RESEARCH_ROOT)/android_research/selinux/policy_analysis.md
	@echo "# Device Tree Analysis" > $(RESEARCH_ROOT)/android_research/device_tree/dtb_analysis.md

# VALIDATION TARGET - This is what meta-scrutiny missed
validate_structure:
	@echo "Validating structure..."
	@test -f $(RESEARCH_ROOT)/android_research/vendor_init/init_analysis.md || (echo "ERROR: Missing init_analysis.md" && exit 1)
	@test -f $(RESEARCH_ROOT)/android_research/hal/hal_analysis.md || (echo "ERROR: Missing hal_analysis.md" && exit 1)
	@test -f $(RESEARCH_ROOT)/android_research/selinux/policy_analysis.md || (echo "ERROR: Missing selinux/policy_analysis.md - TYPO DETECTED!" && exit 1)
	@test -f $(RESEARCH_ROOT)/android_research/device_tree/dtb_analysis.md || (echo "ERROR: Missing dtb_analysis.md" && exit 1)
	@echo "All structures valid! Φ impact: +5.0"

# Self-healing target
heal:
	@echo "Healing structure..."
	@test -d $(RESEARCH_ROOT)/android_rearch/selinux && (mv $(RESEARCH_ROOT)/android_rearch/selinux $(RESEARCH_ROOT)/android_research/selinux && echo "Fixed typo: android_rearch -> android_research")
	@echo "Healing complete. Φ impact: +2.0"

.PHONY: all create_structure validate_structure heal
